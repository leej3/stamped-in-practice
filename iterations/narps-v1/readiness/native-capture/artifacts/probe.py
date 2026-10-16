#!/usr/bin/env python3
"""Host-only checks for John's approved formal-study resources.

No credentials or environment dumps are collected. Native and HPC checks only
read existing evidence/services; annex-round-trip uploads one tiny new payload.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import time
import uuid

REPOSITORY = Path('/Users/johnlee/code/CON/stamped-in-practice')
REPOSITORY_SLUG = 'leej3/stamped-in-practice'
MANIFEST = REPOSITORY / 'pixi.toml'
STATE = Path('/Users/johnlee/.local/state/stamped-in-practice')
NATIVE_RECEIPT = STATE / 'native-session.json'
PREPARATION = Path('/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015')
ENTIRE = '/opt/homebrew/bin/entire'
ANNEX_GIT_URL = 'https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git'
ANNEX_URL = 'annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp'
ANNEX_UUID = '6215ce45-8f0f-4062-9bc0-d04781b4cd11'
HPC_JOB = '65726805'


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


class Probe:
    def __init__(self, name):
        self.artifacts = Path(os.environ['READINESS_ARTIFACT_DIR']).resolve()
        self.commands = []
        self.started = time.monotonic()
        self.report = {
            'schema_version': 1, 'check': name, 'started_at': now(),
            'passed': False, 'observations': {}, 'sources': [], 'limitations': [],
        }
        self.artifacts.mkdir(parents=True, exist_ok=True, mode=0o700)
        shutil.copyfile(__file__, self.artifacts / 'probe.py')
        self.report['probe_sha256'] = sha((self.artifacts / 'probe.py').read_bytes())
        (self.artifacts / 'commands').mkdir()
        dump(self.artifacts / 'commands.json', self.commands)
        dump(self.artifacts / 'verification.json', self.report)

    def require(self, value, message):
        if not value:
            raise ValueError(message)

    def source(self, path, retained_name=None, parse=True):
        data = path.read_bytes()
        record = {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}
        if retained_name:
            destination = self.artifacts / 'sources' / retained_name
            destination.parent.mkdir(exist_ok=True, mode=0o700)
            destination.write_bytes(data)
            record['retained_path'] = str(destination.relative_to(self.artifacts))
        self.report['sources'].append(record)
        return json.loads(data) if parse else data

    def run(self, argv, cwd=None, allowed=(0,), timeout=45, env=None):
        argv = [str(x) for x in argv]
        directory = Path(cwd or self.artifacts).resolve()
        sequence = len(self.commands) + 1
        prefix = f'commands/{sequence:03d}'
        entry = {'argv': argv, 'cwd': str(directory), 'started_at': now(),
                 'stdout': prefix + '.stdout.txt', 'stderr': prefix + '.stderr.txt'}
        self.commands.append(entry)
        dump(self.artifacts / 'commands.json', self.commands)
        started = time.monotonic()
        try:
            response = subprocess.run(argv, cwd=directory, capture_output=True, timeout=timeout, env=env)
            stdout, stderr = response.stdout, response.stderr
            entry['returncode'] = response.returncode
        except subprocess.TimeoutExpired as error:
            stdout, stderr = error.stdout or b'', error.stderr or b''
            entry.update(returncode=None, error=f'Command timed out after {timeout} seconds')
        except OSError as error:
            stdout, stderr = b'', str(error).encode()
            entry.update(returncode=None, error=str(error))
        for name, data in (('stdout', stdout), ('stderr', stderr)):
            (self.artifacts / entry[name]).write_bytes(data)
            entry[name + '_sha256'] = sha(data)
            entry[name + '_bytes'] = len(data)
        entry.update(finished_at=now(), elapsed_seconds=time.monotonic() - started)
        dump(self.artifacts / 'commands.json', self.commands)
        self.require(entry['returncode'] in allowed,
                     f'Command {sequence} failed: {entry.get("error", entry["returncode"])}')
        return stdout.decode('utf-8'), entry['returncode']

    def git(self, repo, *args, **kwargs):
        return self.run(['git', '-C', repo, *args], **kwargs)[0].strip()

    def annex(self, repo, *args, **kwargs):
        return self.run(['pixi', 'run', '--locked', '--manifest-path', MANIFEST,
                         'git', '-C', repo, 'annex', *args], **kwargs)[0].strip()

    def finish(self, error=None):
        self.report.update(finished_at=now(), elapsed_seconds=time.monotonic() - self.started,
                           passed=error is None)
        if error is not None:
            self.report['error'] = str(error)
        dump(self.artifacts / 'verification.json', self.report)
        print(json.dumps({'check': self.report['check'], 'passed': self.report['passed'],
                          'verification': str(self.artifacts / 'verification.json'),
                          'error': self.report.get('error')}))
        return 0 if error is None else 1


def session_record(p, metadata, session_id, checkpoint_id, branch, label):
    p.require(metadata.get('checkpoint_id') == checkpoint_id, label + ' checkpoint identity mismatch')
    p.require(metadata.get('branch') == branch, label + ' checkpoint branch mismatch')
    sessions = [item for item in metadata.get('sessions', []) if item.get('session_id') == session_id]
    p.require(len(sessions) == 1, label + ' expected unique native session is absent')
    session = sessions[0]
    p.require(session.get('agent', '').lower() == 'codex', label + ' session is not Codex')
    p.require(all(session.get(key) for key in ('model', 'created_at', 'turn_id', 'files_touched')),
              label + ' native session metadata is incomplete')
    return session


def native(p):
    p.report['limitations'] = [
        'Re-verifies one retained formal-repository native session; starts no new session and publishes nothing.',
        'Checks the dedicated code branch and immutable commit, not the current checkout HEAD.',
        'Authenticated hosted metadata and current Git refs prove availability now, not all future sessions.',
        'Native event bytes are hashed and inspected but not copied into readiness evidence.',
    ]
    p.require(NATIVE_RECEIPT.is_file(),
              'Native capture receipt is missing: ' + str(NATIVE_RECEIPT) +
              '; create it after completing and publishing the dedicated formal capture session.')
    saved = p.source(NATIVE_RECEIPT, 'native-session.json')
    fields = ('repository_path', 'repository_slug', 'code_commit', 'code_branch',
              'checkpoint_id', 'checkpoint_ref', 'checkpoint_oid', 'session_id', 'native_events_path')
    p.require(all(isinstance(saved.get(key), str) and saved[key] for key in fields),
              'Native capture receipt lacks a required nonempty string field')
    repo = Path(saved['repository_path']).expanduser().resolve()
    p.require(repo == REPOSITORY and saved['repository_slug'] == REPOSITORY_SLUG,
              'Native capture receipt does not identify the formal repository')
    code, branch = saved['code_commit'], saved['code_branch']
    checkpoint, checkpoint_ref = saved['checkpoint_id'], saved['checkpoint_ref']
    checkpoint_oid, session_id = saved['checkpoint_oid'], saved['session_id']
    p.require(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', code), 'Invalid native code commit')
    p.require(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', checkpoint_oid), 'Invalid checkpoint commit')
    p.require(re.fullmatch(r'[A-Za-z0-9]{26}', checkpoint), 'Invalid checkpoint identifier')
    p.require(re.fullmatch(r'[A-Za-z0-9-]+', session_id), 'Invalid native session identifier')
    p.require(branch.startswith('codex/'), 'Use a dedicated codex/ capture branch')
    code_ref = 'refs/heads/' + branch
    p.git(repo, 'check-ref-format', code_ref)
    p.require(checkpoint_ref == f'refs/entire/checkpoints/{checkpoint[-2:]}/{checkpoint}',
              'Checkpoint ref does not match checkpoint identifier')
    events_path = Path(saved['native_events_path']).expanduser()
    p.require(events_path.is_absolute() and events_path.is_file(), 'Native event stream is missing')
    event_bytes = p.source(events_path, parse=False)
    events = [json.loads(line) for line in event_bytes.splitlines() if line.strip()]
    p.require(events and all(isinstance(event, dict) for event in events), 'Invalid native event stream')
    session_ids = {event.get('thread_id') for event in events if event.get('type') == 'thread.started'}
    p.require(session_ids == {session_id}, 'Native event stream has missing or unexpected session identities')
    terminal = [event['type'] for event in events if event.get('type') in ('turn.completed', 'turn.failed')]
    p.require(terminal and terminal[-1] == 'turn.completed', 'Native event stream lacks a final completed turn')
    p.require(any(event.get('type') == 'item.completed' for event in events),
              'Native event stream has no completed work item')
    p.require(p.git(repo, 'rev-parse', code + '^{commit}') == code, 'Recorded code commit is absent')
    p.require(p.git(repo, 'rev-parse', code_ref) == code, 'Dedicated local capture branch moved or is absent')
    message = p.git(repo, 'show', '-s', '--format=%B', code)
    p.require(re.search(r'^Entire-Checkpoint: ' + re.escape(checkpoint) + r'$', message, re.MULTILINE),
              'Code commit lacks matching checkpoint trailer')
    p.require('Co-Authored-By: Codex Desktop ' in message and 'Codex-Reasoning-Effort: ' in message
              and 'unavailable' not in message, 'Code commit lacks resolved Codex provenance trailers')
    p.require(p.git(repo, 'rev-parse', checkpoint_ref) == checkpoint_oid,
              'Local checkpoint ref does not match receipt')
    local_text, _ = p.run([ENTIRE, 'checkpoint', 'explain', '--commit', code, '--json'], cwd=repo)
    local = json.loads(local_text)
    local_session = session_record(p, local, session_id, checkpoint, branch, 'Local')
    changed = set(p.git(repo, 'diff-tree', '--root', '--no-commit-id', '--name-only', '-r', code).splitlines())
    touched = local_session['files_touched']
    p.require(isinstance(touched, list) and all(isinstance(path, str) for path in touched),
              'Checkpoint touched-file inventory is invalid')
    matching = sorted(changed.intersection(touched))
    p.require(matching, 'No checkpoint-touched file is present in the capture commit changes')
    if 'code_file' in saved:
        p.require(saved['code_file'] in matching, 'Requested capture file is absent from commit/checkpoint changes')
        matching = [saved['code_file']]
    file_records = []
    for name in matching:
        path = PurePosixPath(name)
        p.require(not path.is_absolute() and '..' not in path.parts and '.git' not in path.parts,
                  'Invalid checkpoint file path')
        kind = p.git(repo, 'cat-file', '-t', code + ':' + name)
        p.require(kind == 'blob', 'Capture checkpoint file is not a committed blob')
        oid = p.git(repo, 'rev-parse', code + ':' + name)
        file_records.append({'path': name, 'git_blob': oid})
    ssh_remote = 'git@github.com:' + REPOSITORY_SLUG + '.git'
    refs, _ = p.run(['git', 'ls-remote', '--refs', ssh_remote, code_ref, checkpoint_ref], cwd=repo)
    remote = {line.split()[1]: line.split()[0] for line in refs.splitlines() if line.strip()}
    p.require(remote == {code_ref: code, checkpoint_ref: checkpoint_oid},
              'Published code/checkpoint refs do not match native receipt')
    # Entire prefers local checkpoints even with --repo when cwd is that repo.
    # An empty independent Git context forces the hosted path; the CLI requires
    # Git context and rejects a plain temporary directory. Strip inherited Git
    # selectors so they cannot redirect that context back to the source checkout.
    hosted_context = p.artifacts / 'hosted-read-context'
    hosted_env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    p.run(['git', 'init', '--quiet', hosted_context], env=hosted_env)
    hosted_text, _ = p.run([ENTIRE, 'checkpoint', 'explain', checkpoint,
                            '--repo', 'gh/' + REPOSITORY_SLUG, '--json'],
                           cwd=hosted_context, env=hosted_env)
    hosted = json.loads(hosted_text)
    p.require(hosted.get('checkpoint_id') == checkpoint, 'Hosted checkpoint identity mismatch')
    hosted_sessions = [item for item in hosted.get('sessions', [])
                       if item.get('session_id') == session_id]
    p.require(len(hosted_sessions) == 1, 'Hosted expected unique native session is absent')
    hosted_session = hosted_sessions[0]
    # Hosted summaries omit branch and turn_id; those are checked locally above.
    session_fields = ('agent', 'model', 'created_at', 'files_touched')
    p.require(all(local_session[key] == hosted_session.get(key) for key in session_fields),
              'Hosted native session metadata differs from matching local checkpoint')
    p.report['observations'] = {
        'repository_path': str(repo), 'repository_slug': REPOSITORY_SLUG,
        'code_commit': code, 'code_branch': branch, 'checkpoint_id': checkpoint,
        'checkpoint_ref': checkpoint_ref, 'checkpoint_oid': checkpoint_oid,
        'session_id': session_id, 'remote_refs': remote, 'committed_files': file_records,
        'event_count': len(events), 'completed_turns': terminal.count('turn.completed'),
        'native_turn_completed': True, 'hosted_metadata_matches': True,
        'current_checkout_head_required': False,
        'hosted_read_context': str(hosted_context),
        'hosted_comparison_fields': list(session_fields),
        'hosted_git_environment_stripped': True,
    }


def annex_round_trip(p):
    p.report['limitations'] = [
        'Uploads one tiny synthetic artifact to the existing approved CON Hub store; does not test all study inputs or capacity.',
        'Keeps both independent local repositories and remote payload; publishes no Git branches and deletes nothing.',
        'Uses the formal clone Pixi manifest and existing host credential provider without collecting credentials.',
    ]
    p.require(MANIFEST.is_file() and MANIFEST.with_name('pixi.lock').is_file(),
              'Formal clone manifest and validated working lock are required for annex checks')
    for path in (MANIFEST, MANIFEST.with_name('pixi.lock')):
        p.source(path, parse=False)
    working = STATE / ('annex-readiness-' + uuid.uuid4().hex)
    working.mkdir(parents=True, mode=0o700)
    donor, recipient = working / 'donor', working / 'recipient'
    p.report['observations'].update(donor=str(donor), recipient=str(recipient),
                                  remote_git_url=ANNEX_GIT_URL, annex_url=ANNEX_URL,
                                  remote_uuid=ANNEX_UUID)
    for repo in (donor, recipient):
        repo.mkdir(mode=0o700)
        p.git(repo, 'init', '--quiet')
        p.annex(repo, 'init', 'formal-readiness-' + repo.name)
        p.git(repo, 'remote', 'add', 'con-hub', ANNEX_GIT_URL)
        p.git(repo, 'config', 'remote.con-hub.annexurl', ANNEX_URL)
        p.git(repo, 'config', 'remote.con-hub.annex-uuid', ANNEX_UUID)
    payload = (json.dumps({'purpose': 'STAMPED formal host readiness round trip', 'created_at': now(),
                           'nonce': str(uuid.uuid4())}, sort_keys=True) + '\n').encode()
    name = 'readiness-artifact.json'
    (donor / name).write_bytes(payload)
    (p.artifacts / 'payload.json').write_bytes(payload)
    p.annex(donor, 'add', '--backend=SHA256E', '--force', '--', name)
    key = p.annex(donor, 'lookupkey', '--', name)
    p.require(key == f'SHA256E-s{len(payload)}--{sha(payload)}.json', 'New annex key does not match payload')
    p.annex(donor, 'copy', '--to', 'con-hub', '--', name, timeout=90)
    p.annex(donor, 'checkpresentkey', key, 'con-hub')
    p.annex(recipient, 'fromkey', '--force', key, name)
    p.require(not (recipient / name).exists(), 'Recipient unexpectedly had payload before remote transfer')
    p.require(not any((recipient / '.git/objects/info' / path).exists()
                      for path in ('alternates', 'http-alternates')), 'Recipient shares a Git object store')
    donor_uuid = p.git(donor, 'config', 'annex.uuid')
    recipient_uuid = p.git(recipient, 'config', 'annex.uuid')
    p.require(donor_uuid and recipient_uuid and donor_uuid != recipient_uuid,
              'Donor and recipient are not independent annex repositories')
    p.annex(recipient, 'transferkey', key, '--from', 'con-hub', timeout=90)
    actual = (recipient / name).read_bytes()
    p.require(actual == payload, 'Independent remote retrieval bytes differ')
    p.require((recipient / name).resolve().is_relative_to(recipient / '.git/annex/objects'),
              'Recipient payload resolves outside its independent annex store')
    p.report['observations'].update({
        'payload_bytes': len(payload), 'payload_sha256': sha(payload), 'annex_key': key,
        'donor_uuid': donor_uuid, 'recipient_uuid': recipient_uuid,
        'recipient_payload': str((recipient / name).resolve()),
        'new_upload_command_succeeded': True, 'remote_presence_rechecked': True,
        'recipient_absent_before_transfer': True, 'independent_bytes_identical': True,
    })


def hpc(p):
    p.report['limitations'] = [
        'Re-verifies existing Unity job 65726805; submits no new job and writes no remote files.',
        'Demonstrates the retained small CPU scheduler/output path, not present queue admission or scientific workload readiness.',
    ]
    submission = p.source(PREPARATION / 'hpc-submit.json', 'hpc-submit.json')
    prior = p.source(PREPARATION / 'hpc-verify.json', 'hpc-verify.json')
    p.require(submission.get('returncode') == 0 and submission.get('stdout', '').strip() == HPC_JOB
              and prior.get('job_id') == HPC_JOB and prior.get('returncode') == 0 and prior.get('passed') is True,
              'Original successful submission and verification identities are missing or inconsistent')
    remote_directory = submission['remote_directory']
    p.require(re.fullmatch(r'/work/[A-Za-z0-9_/-]+', remote_directory), 'Unexpected remote directory')
    ssh = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', 'unity']
    accounting, _ = p.run(ssh + ['sacct -n -P -j ' + HPC_JOB + ' --format=JobIDRaw,State,ExitCode,Elapsed,NodeList'])
    records = [line.split('|') for line in accounting.splitlines() if line.strip()]
    matches = [row for row in records if len(row) >= 5 and row[0] == HPC_JOB]
    p.require(len(matches) == 1 and matches[0][1] == 'COMPLETED' and matches[0][2] == '0:0',
              'Current sacct does not prove successful completion of the retained job')
    output, _ = p.run(ssh + ['cat ' + remote_directory + '/job-' + HPC_JOB + '.out'])
    errors, _ = p.run(ssh + ['cat ' + remote_directory + '/job-' + HPC_JOB + '.err'])
    lines = output.splitlines()
    p.require(len(lines) == 2 and lines[1] == 'stamped-readiness-ok', 'Completed job output marker is missing or unexpected')
    p.require(lines[0] == matches[0][4], 'Job hostname and accounting node do not match')
    p.require(not errors.strip(), 'Job stderr is nonempty')
    p.report['observations'] = {'job_id': HPC_JOB, 'scheduler_record': matches[0],
                                'remote_directory': remote_directory, 'output': lines,
                                'stderr_empty': True, 'new_jobs_submitted': 0,
                                'original_submission_and_verification_retained': True}


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=('native-capture', 'annex-round-trip', 'hpc-round-trip'))
    args = parser.parse_args()
    probe = Probe(args.check)
    functions = {'native-capture': native, 'annex-round-trip': annex_round_trip, 'hpc-round-trip': hpc}
    try:
        functions[args.check](probe)
    except Exception as error:
        return probe.finish(error)
    return probe.finish()


if __name__ == '__main__':
    sys.exit(main())

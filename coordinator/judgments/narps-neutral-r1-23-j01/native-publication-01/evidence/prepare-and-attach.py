"""Publish an ended judge's existing native capture from a separate copy."""
from pathlib import Path
from datetime import datetime, timezone
import collections
import hashlib
import json
import os
import shutil
import subprocess
import traceback

root = Path(__file__).resolve().parent
judgment = root.parent.parent
capture = root.parent / 'late-capture-01'
repo = root / 'publisher'
repo.mkdir()
base = '36562e3069d864dcfc295d79a7017c9a4081b00a'
branch = 'codex/narps-neutral-r1-23-j01-native-publication'
relative = Path('coordinator/judgments/narps-neutral-r1-23-j01/native-publication-01')
main = Path('/Users/johnlee/code/CON/stamped-in-practice')
pixi = ['pixi', 'run', '--manifest-path', str(main/'pixi.toml'), '--locked']
resolver = '/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'
host = json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_text())
native_path = judgment / 'attempt-01/native/result.json'
native = json.loads(native_path.read_text())
session, = native['native_session_ids']
original_workspace = Path(native['judge_workspace'])
metadata_path = original_workspace / '.git/entire-sessions' / (session+'.json')
metadata = json.loads(metadata_path.read_text())
assert metadata['phase'] == 'ended' and metadata['session_id'] == session
raw_path = Path(metadata['transcript_path'])
sources = [native_path, metadata_path, raw_path, judgment/'dispatch.json']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {str(p): sha(p) for p in sources}
assert raw_path.read_bytes() == (capture/'native/native-transcript.jsonl').read_bytes()
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
commands = []

def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')

def run(label, argv, override=None, allow=False):
    argv = list(map(str, argv))
    p = subprocess.run(argv, cwd=repo, env=override or env, capture_output=True)
    (root/(label+'.stdout')).write_bytes(p.stdout)
    (root/(label+'.stderr')).write_bytes(p.stderr)
    commands.append({'label':label, 'argv':argv, 'cwd':str(repo), 'returncode':p.returncode,
                     'stdout':label+'.stdout', 'stderr':label+'.stderr'})
    save(root/'commands.json', commands)
    if not allow: p.check_returncode()
    return p.stdout

def git(label, *args):
    return run(label, ['git', *args]).decode().strip()

def identity(data):
    records = [json.loads(line) for line in data.splitlines()]
    meta = [r['payload'] for r in records if r.get('type')=='session_meta']
    assert any(r.get('id')==session and r.get('cwd')==str(original_workspace) for r in meta)
    return [(r.get('type'), r.get('timestamp'), r.get('payload',{}).get('type'),
             r.get('payload',{}).get('id'), r.get('payload',{}).get('thread_id'),
             r.get('payload',{}).get('turn_id'), r.get('payload',{}).get('item',{}).get('type'),
             r.get('payload',{}).get('item',{}).get('id')) for r in records]

try:
    git('init', 'init', '--template=', '--initial-branch', branch)
    git('remote', 'remote', 'add', 'origin', 'https://github.com/leej3/stamped-in-practice.git')
    git('push-remote', 'remote', 'set-url', '--push', 'origin', 'git@github.com:leej3/stamped-in-practice.git')
    git('ignore-origin-annex', 'config', 'remote.origin.annex-ignore', 'true')
    git('fetch-base', 'fetch', '--no-tags', 'origin', base)
    git('checkout-base', 'reset', '--hard', 'FETCH_HEAD')
    assert git('base-head', 'rev-parse', 'HEAD') == base
    assert not (repo/'.git/objects/info/alternates').exists()
    run('annex-init', pixi+['git','annex','init','judge23-j01 native capture publisher'])
    git('hub', 'remote','add',host['annex_remote'],host['annex_git_url'])
    git('hub-route','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url'])
    git('fetch-annex','fetch','origin','git-annex:refs/remotes/origin/git-annex')
    run('merge-annex',pixi+['git','annex','merge'])
    dest = repo/relative
    dest.mkdir(parents=True)
    copied = {}
    for name, source in [('raw-native-transcript.jsonl',capture/'native/native-transcript.jsonl'),
                         ('original-shadow-full.jsonl',capture/'native/shadow-00-full.jsonl'),
                         ('original-capture-verification.json',capture/'native/verification.json'),
                         ('native-result.json',native_path),('entire-session.json',metadata_path)]:
        shutil.copy2(source,dest/name)
        assert sha(source)==sha(dest/name)
        copied[name]={'source':str(source),'sha256':sha(source),'bytes':source.stat().st_size}
    save(dest/'source.json',{'kind':'coordinator-native-judge-publication','judgment':judgment.name,
         'session_id':session,'base_commit':base,'original_judge_workspace':str(original_workspace),
         'late_capture_manifest_sha256':sha(capture/'manifest.json'),'files':copied,
         'method':'Historical attachment for publication of an already ended, live-captured judge session; no new native session or scientific assessment.',
         'attribution':'Coordinator preservation. Original native history and original processed shadow are retained separately.'})
    (dest/'README.md').write_text('# Native assessment session\n\n'
       'These are coordinator publication records for the completed judge session.\n'
       'The [raw native transcript](raw-native-transcript.jsonl) and '
       '[original Entire shadow](original-shadow-full.jsonl) retain their separate representations.\n'
       'Their [source record](source.json) binds exact bytes and the original late capture.\n'
       'A later coordinator commit attaches the existing session for hosted publication; '
       'this is not a new assessment or evidence that publication occurred during the original session.\n'
       'Use the [retrieval guide](https://github.com/leej3/stamped-in-practice/blob/main/RETRIEVAL.md) '
       'for annex payloads.\n')
    annex = [str(relative/n) for n in ['raw-native-transcript.jsonl','original-shadow-full.jsonl']]
    with (repo/'.gitattributes').open('a') as f:
        f.write('\n# Coordinator native judge transcript payloads.\n')
        for path in annex:f.write(json.dumps('/'+path)+' annex.largefiles=anything annex.backend=SHA256E\n')
    run('annex-transcripts',pixi+['git','annex','add','--force-large','--backend=SHA256E','--',*annex])
    for path in annex:
        copied[Path(path).name]['annex_key']=git('key-'+Path(path).stem,'annex','lookupkey',path)
    save(root/'payloads.json',copied)
    snapper=pixi+['pre-commit','run','--config',str(main/'.pre-commit-config.yaml'),'snapper','--files',str(relative/'README.md')]
    run('snapper',snapper,allow=True)
    run('snapper-check',snapper)
    git('stage','add','--force','--','.gitattributes',str(relative))
    git('diff-check','diff','--cached','--check')
    assert not git('check-originals','diff','--cached','--name-only','--','input','coordinator/delivery-01','coordinator/original-manifest.json')
    trailers=run('commit-provenance',[resolver]).decode().strip()
    assert 'Co-Authored-By: ' in trailers and 'Codex-Reasoning-Effort: ' in trailers
    message=root/'commit-message.txt'
    message.write_text('chore(provenance): retain the completed judge23-j01 native session\n\n'
        'Preserve raw native history and the original processed shadow separately.\n'
        'Later coordinator attachment publishes the existing session without\n'
        'changing the judged delivery or awarding worker-practice credit.\n\n'+trailers+'\n')
    git('commit','-c','core.hooksPath=/dev/null','commit','-F',str(message))
    pre_attach=git('pre-attachment-head','rev-parse','HEAD')
    tree=git('pre-attachment-tree','rev-parse','HEAD^{tree}')
    git('retain-pre-attachment','update-ref','refs/retained/pre-attachment/'+session,pre_attach)
    with (repo/'.git/info/exclude').open('a') as f:f.write('\n/.entire/\n/.codex/\n')
    run('enable',['entire','enable','--local','--agent','codex','--no-init-repo','--checkpoint-backend','refs','--checkpoint-remote','github:leej3/stamped-in-practice','--skip-push-sessions','--telemetry=false','--absolute-git-hook-path'])
    run('configure',['entire','configure','--local','--skip-push-sessions=false'])
    fresh=run('attach-provenance',[resolver]).decode().strip()
    assert fresh==trailers
    attachenv=dict(env,CODEX_HOME=native['codex_home'],GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='core.hooksPath',GIT_CONFIG_VALUE_0='/dev/null')
    save(root/'attach-environment.json',{'CODEX_HOME':native['codex_home'],'core.hooksPath':'/dev/null','meaning':'Separate publisher; historical attachment only. No original source hooks invoked.'})
    run('attach',['entire','session','attach',session,'--agent','codex','--force'],attachenv)
    head=git('attached-head','rev-parse','HEAD')
    assert git('attached-tree','rev-parse','HEAD^{tree}')==tree
    msg=git('attached-message','show','-s','--format=%B','HEAD')
    assert all(line in msg for line in fresh.splitlines())
    checkpoint=next(line.split(': ',1)[1] for line in msg.splitlines() if line.startswith('Entire-Checkpoint: '))
    refs=git('checkpoint-refs','for-each-ref','--format=%(refname) %(objectname)','refs/entire/checkpoints').splitlines()
    matching=[line.split() for line in refs if line.split()[0].endswith('/'+checkpoint)]
    assert len(matching)==1
    checkpoint_ref,checkpoint_oid=matching[0]
    processed=run('processed-transcript',['entire','checkpoint','explain',checkpoint,'--transcript'])
    local=json.loads(run('local-checkpoint',['entire','checkpoint','explain',checkpoint,'--json']))
    assert local['checkpoint_id']==checkpoint and session in [s['session_id'] for s in local['sessions']]
    raw=raw_path.read_bytes()
    assert identity(raw)==identity(processed)
    assert {str(p):sha(p) for p in sources}==before
    assert not git('final-status','status','--porcelain')
    save(root/'attachment.json',{'prepared_at':datetime.now(timezone.utc).isoformat(),'base_commit':base,
      'branch':branch,'pre_attachment_commit':pre_attach,'commit':head,'session_id':session,
      'checkpoint_id':checkpoint,'checkpoint_ref':checkpoint_ref,'checkpoint_oid':checkpoint_oid,
      'raw_sha256':hashlib.sha256(raw).hexdigest(),'processed_sha256':hashlib.sha256(processed).hexdigest(),
      'raw_processed_byte_identical':raw==processed,'all_line_identity_fields_equal':True,
      'original_sources_unchanged':before,'historical_attachment':True,'hosted_verified':False,
      'annex_paths':annex,'coordinator_record_path':str(relative)})
    print(json.dumps({'prepared':True,'commit':head,'checkpoint_id':checkpoint,'session_id':session}))
except BaseException:
    (root/'failure.txt').write_text(traceback.format_exc())
    raise

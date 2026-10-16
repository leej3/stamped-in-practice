from pathlib import Path
import collections
import hashlib
import importlib.util
import json
import os
import tarfile

helper = Path.home()/'.config/stamped-in-practice/readiness_probe.py'
spec = importlib.util.spec_from_file_location('probe', helper)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
os.environ['READINESS_ARTIFACT_DIR'] = str(m.STATE/'archive-publication-02')
p = m.Probe('formal-prelaunch-archive-publication-and-independent-retrieval')
try:
    root = m.REPOSITORY
    rel = Path('iterations/narps-v1/evidence/prelaunch-evidence-01.tar.gz')
    archive = root/rel
    retention = p.source(root/rel.parent/'retention.json', 'retention-before.json')
    inventory = p.source(root/rel.parent/'archive-inventory.json', 'archive-inventory.json')
    p.source(root/'iterations/narps-v1/procedure.json', 'procedure.json')
    baseline_index = p.git(root, 'ls-files', '--stage', '--', rel, 'assets/workbench.pdf')
    baseline_procedure = m.sha((root/'iterations/narps-v1/procedure.json').read_bytes())
    donor_uuid = p.git(root, 'config', 'annex.uuid')
    key = p.annex(root, 'lookupkey', '--', rel)
    expected = retention['archive_sha256']
    p.require(key == retention['annex_key'] and m.sha(archive.read_bytes()) == expected,
              'Archive key or source content does not match retained inventory')
    p.run(['/Users/johnlee/.local/bin/agent-vault', 'check',
           'hub.centerforopenneuroscience.org', 'leej3', '--cached-only'])
    remote = retention['annex_remote']
    names = p.git(root, 'remote').splitlines()
    if 'con-hub' not in names:
        p.git(root, 'remote', 'add', 'con-hub', remote['git_url'])
    else:
        p.require(p.git(root, 'remote', 'get-url', 'con-hub') == remote['git_url'],
                  'Existing con-hub remote differs from declared store')
    p.git(root, 'config', 'remote.con-hub.annexurl', remote['annex_url'])
    p.git(root, 'config', 'remote.con-hub.annex-uuid', remote['uuid'])
    p.annex(root, 'copy', '--to', 'con-hub', '--', rel, timeout=120)
    p.annex(root, 'checkpresentkey', key, 'con-hub')
    recipient = p.artifacts/'independent-recipient'
    recipient.mkdir(mode=0o700)
    p.git(recipient, 'init', '--quiet')
    p.annex(recipient, 'init', 'formal-prelaunch-evidence-independent-recipient')
    p.git(recipient, 'remote', 'add', 'con-hub', remote['git_url'])
    p.git(recipient, 'config', 'remote.con-hub.annexurl', remote['annex_url'])
    p.git(recipient, 'config', 'remote.con-hub.annex-uuid', remote['uuid'])
    recipient_uuid = p.git(recipient, 'config', 'annex.uuid')
    p.require(donor_uuid != recipient_uuid, 'Recipient annex identity is not independent')
    p.require(not any((recipient/'.git/objects/info'/n).exists()
                     for n in ('alternates', 'http-alternates')), 'Recipient has object alternates')
    output = recipient/'prelaunch-evidence-01.tar.gz'
    p.annex(recipient, 'fromkey', '--force', key, output.name)
    p.require(not output.exists(), 'Recipient payload already existed before transfer')
    p.annex(recipient, 'transferkey', key, '--from', 'con-hub', timeout=120)
    p.require(output.resolve().is_relative_to(recipient/'.git/annex/objects'),
              'Payload resolves outside independent recipient store')
    content = output.read_bytes()
    p.require(m.sha(content) == expected and content == archive.read_bytes(),
              'Independently retrieved archive bytes differ')
    p.require(len(content) == inventory['archive_bytes'], 'Archive size mismatch')
    rows = {r['path']: r for r in inventory['files']}
    p.require(len(rows) == len(inventory['files']) == retention['source_file_entries'] == 471,
              'Unexpected archive inventory count')
    file_count = link_count = 0
    with tarfile.open(output, 'r:gz') as tar:
        entries = [entry for entry in tar.getmembers() if not entry.isdir()]
        paths = [entry.name.removeprefix('prelaunch-evidence/') for entry in entries]
        p.require(len(paths) == len(set(paths)) and set(paths) == set(rows),
                  'Retrieved archive entry set differs from inventory')
        for entry, name in zip(entries, paths):
            row = rows[name]
            if entry.issym():
                link_count += 1
                p.require(entry.linkname == row['link'], 'Archived symlink mismatch: '+name)
            else:
                p.require(entry.isfile(), 'Unexpected archive member type: '+name)
                file_count += 1
                data = tar.extractfile(entry).read()
                p.require(len(data) == row['bytes'] and m.sha(data) == row['sha256'],
                          'Archived file mismatch: '+name)
    p.report['observations'].update({
        'archive_key': key, 'archive_sha256': expected, 'archive_bytes': len(content),
        'remote_store': remote, 'upload_succeeded': True, 'remote_presence_rechecked': True,
        'donor_uuid': donor_uuid, 'recipient_uuid': recipient_uuid,
        'recipient': str(recipient), 'recipient_payload': str(output.resolve()),
        'recipient_absent_before_transfer': True, 'recipient_has_no_alternates': True,
        'independent_bytes_identical': True, 'archive_regular_files_verified': file_count,
        'archive_symlinks_verified': link_count, 'archive_inventory_entries_verified': len(entries),
    })
    # The original PDF is already registered at the same store. Retrieve only
    # its recorded key; do not re-add or alter the original asset.
    asset = Path('assets/workbench.pdf')
    asset_metadata = json.loads(p.annex(root, 'whereis', '--json', '--', asset))
    m.dump(p.artifacts/'workbench-original-annex-metadata.json', asset_metadata)
    asset_key = asset_metadata['key']
    p.require(any(row['uuid'] == remote['uuid'] for row in asset_metadata['whereis']),
              'Original asset metadata does not identify declared annex store')
    p.require(asset_key == 'MD5E-s1860551--f448dd555f1edb561096432b3ff5d6be.pdf',
              'Original asset key changed')
    p.annex(root, 'checkpresentkey', asset_key, 'con-hub')
    recovered_asset = recipient/'workbench.pdf'
    p.annex(recipient, 'fromkey', '--force', asset_key, recovered_asset.name)
    p.require(not recovered_asset.exists(), 'Recipient already contained workbench payload')
    p.annex(recipient, 'transferkey', asset_key, '--from', 'con-hub', timeout=120)
    pdf = recovered_asset.read_bytes()
    p.require(len(pdf) == 1860551 and hashlib.md5(pdf).hexdigest() == 'f448dd555f1edb561096432b3ff5d6be',
              'Original asset content does not match its MD5E identity')
    p.require(recovered_asset.resolve().is_relative_to(recipient/'.git/annex/objects'),
              'Asset resolves outside independent recipient')
    p.report['observations']['original_asset'] = {
        'path': str(asset), 'key': asset_key, 'bytes': len(pdf), 'sha256': m.sha(pdf),
        'md5_matches_key': True, 'independent_retrieval_verified': True,
        'recipient_payload': str(recovered_asset.resolve()), 'original_asset_modified': False,
    }
    p.require(p.git(root, 'ls-files', '--stage', '--', rel, asset) == baseline_index,
              'Archive or original asset index entry changed')
    p.require(m.sha((root/'iterations/narps-v1/procedure.json').read_bytes()) == baseline_procedure,
              'Frozen procedure changed')
    p.report['limitations'] = [
        'Verifies only the retained prelaunch archive and original workbench PDF; no scientific outputs or future uploads are covered.',
        'Repository annex remote configuration and native annex location metadata were updated; no tracked files, task commits or Git refs were pushed.',
        'Existing host credential helper consumed cached credentials privately; no unlock or credential export was performed.',
    ]
    p.finish()
except Exception as error:
    p.finish(error)
    raise

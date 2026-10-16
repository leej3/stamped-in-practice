from pathlib import Path
import hashlib
import json
import shutil

P = Path(__file__).resolve().parent
B = P.parent
D = B / 'dataset'
sha = lambda data: hashlib.sha256(data).hexdigest()
copies = []
def copy(source, destination):
    data = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    assert not destination.exists()
    shutil.copy2(source, destination)
    assert source.read_bytes() == data == destination.read_bytes()
    copies.append({'source': str(source), 'destination': str(destination.relative_to(D)), 'sha256': sha(data), 'bytes': len(data)})

packages = [
    ('assessment-context-native-trial-package-01', 'measurement-development/assessment-context-native-trial-01'),
    ('assessment-context-development-package-01', 'measurement-development/assessment-context-development-01'),
    ('operational-support-publication-retention-01', 'measurement-development/operational-support-publication-01'),
]
for source_name, destination_name in packages:
    source = B / source_name
    destination = D / destination_name
    assert not destination.exists()
    destination.mkdir()
    for path in sorted(source.iterdir()):
        if not path.is_file():
            assert path.name == 'content', path
            continue
        name = 'SOURCE-README.txt' if path.name == 'README.md' else path.name
        copy(path, destination / name)
    if (source / 'README.md').exists():
        (destination / 'README.md').write_bytes((source / 'README.md').read_bytes())

support = D / 'measurement-development/operational-support-publication-01'
for path in sorted((B / 'operational-support-publication-agent-session-01').iterdir()):
    assert path.is_file()
    copy(path, support / 'coordinator-session' / path.name)

development = D / 'measurement-development/assessment-context-development-01'
(development / 'README.md').write_text('''# Context projection development and integration

The archive preserves the reviewed context projection, replay precondition and
formal-response safeguards, their tests, the supplied-file audit, the prospective
boundary plan and the integration commands. The engineer's complete closed
native session is included. There are no exclusions from these four evidence
directories.

Runtime source `b6dfd55cef04393c5deb990c5f57fcad2118bbf0` was integrated into main
at `80cd94bdf80896d7cb0df4b7ba4eb11f561ad838` without synthetic fixture changes.
All nine candidate files remained byte-identical. The additional task-only change
routes the projection and operational tests through `launcher-tests`: 330 passed,
one skipped. The existing formal sources, seals and results remain unchanged.

See the [one native synthetic trial](../assessment-context-native-trial-01/README.md)
for the actual restricted environment, preserved original delivery, genuine replay
and retained command failures. This development evidence does not authorize a new
formal launch. Scientific-category and generic skill candidates are separate.

The annexed `development.tar.gz` is verified locally against every archived file,
mode and literal link. Hub upload and independent payload retrieval remain
pending; published Git pointers do not establish payload availability.
''')

status = D / 'STATUS.md'
text = status.read_text()
text = text.replace('**Round one and its separately registered reassessment are complete; all further formal launches are held.** The original24 workers are unchanged.', '**Round one and its separately registered reassessment are complete; all further formal launches are held.** The original 24 workers are unchanged.')
text = text.replace('Duplicate judgments disagree on67/248 item comparisons and5/8 scientific categories;', 'Duplicate judgments disagree on 67/248 item comparisons and on scientific adequacy in 5/8 duplicate pairs;')
text = text.replace('future launches await a reviewed context-projection correction and a declared measurement boundary.', 'future launches require a declared measurement boundary. The [reviewed context mechanism and one synthetic native trial](measurement-development/assessment-context-native-trial-01/README.md) are complete; prospective scientific guidance and skill checks remain separate, and no new formal launch is authorized.')
text = text.replace('full-support archives have separate status.', 'all 32 full-support archives are retained locally, with 2 previously retrieved and 30 still Hub-pending. [Every support branch, report and archive identity is linked here](measurement-development/operational-support-publication-01/README.md).')
status.write_text(text)
sessions = D / 'assessment-series/narps-neutral-r1-operational-v4/synthesis/SESSIONS.md'
text = sessions.read_text()
text = text.replace('These counts do not describe the separate full-support archive publication.', 'These counts do not describe the separate full-support archive publication.\n[All 32 support branches, reports and archive pointers](../../../measurement-development/operational-support-publication-01/README.md) are now directly linked: 2 full-support archives were independently retrieved earlier, and 30 are retained locally with Hub transfer pending.')
sessions.write_text(text)
(P / 'source-copies.json').write_text(json.dumps({'copies': copies, 'scope': 'Exact copied source files; authored navigation README and STATUS changes are outside this byte-copy claim.'}, indent=2) + '\n')
copy(P / 'source-copies.json', development / 'publication-source-copies.json')
print(json.dumps({'copied_files': len(copies), 'copied_bytes': sum(row['bytes'] for row in copies)}))

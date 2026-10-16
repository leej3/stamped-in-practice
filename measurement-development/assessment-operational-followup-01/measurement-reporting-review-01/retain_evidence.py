"""Retain only named protocol/preparation sources; never read judgment outcomes."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path('/Users/johnlee/code/CON/stamped-in-practice')
PREP = Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/repaired-series-preparation-01')
OUT = Path(__file__).resolve().parent
SOURCES = {
    'AGENTS.md': ROOT / 'AGENTS.md',
    'comparison-plan.md': ROOT / 'comparison-plan.md',
    'AGGREGATION.md': ROOT / 'scripts/AGGREGATION.md',
    'aggregate_comparison.py': ROOT / 'scripts/aggregate_comparison.py',
    'original-registration.md': ROOT / 'iterations/narps-neutral-v1/registration.md',
    'scientific-judging.md': ROOT / 'iterations/narps-neutral-v1/scientific-judging.md',
    'prompt.md': ROOT / 'prompt.md',
    'registration-draft.md': PREP / 'registration-draft.md',
    'series-draft.json': PREP / 'series-draft.json',
    'original-allocation.json': PREP / 'original-allocation.json',
    'pre-commit-config.yaml': ROOT / '.pre-commit-config.yaml',
}
(OUT / 'sources').mkdir(exist_ok=False)
sources = []
for name, path in SOURCES.items():
    payload = path.read_bytes()
    (OUT / 'sources' / name).write_bytes(payload)
    sources.append({'source': str(path), 'retained': 'sources/' + name,
                    'sha256': sha256(payload).hexdigest(), 'bytes': len(payload)})
series = json.loads((OUT / 'sources/series-draft.json').read_bytes())
allocation_bytes = (OUT / 'sources/original-allocation.json').read_bytes()
allocation = json.loads(allocation_bytes)
round1 = next(r for r in allocation['rounds'] if r['round'] == 1)
fields = ('judgment', 'run', 'role', 'dispatch_order')
slot_identity_matches = [tuple(s[k] for k in fields) for s in series['judgment_dispatch_order']] == [
    tuple(s[k] for k in fields) for s in round1['judgment_dispatch_order']]
condition_by_run = {r['run']: r['condition'] for r in round1['launch_order']}
counts = Counter((condition_by_run[s['run']], s['role']) for s in series['judgment_dispatch_order'])
receipt = {
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Read-only protocol/preparation review; no new-series outcomes, model launches, repository edits, commits or pushes.',
    'repository_head': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
    'repository_status_porcelain': subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain'], text=True),
    'sources': sources,
    'allocation_checks': {
        'declared_allocation_hash_matches': sha256(allocation_bytes).hexdigest() == series['original_allocation_sha256'],
        'round1_slot_identities_roles_and_order_match': slot_identity_matches,
        'round1_workers': len(condition_by_run),
        'round1_assigned_judgments': len(series['judgment_dispatch_order']),
        'round1_preselected_duplicate_objects': len(round1['duplicate_judgments']),
        'per_condition': {c: {role: counts[c, role] for role in ('primary', 'duplicate')} for c in allocation['conditions']},
        'full_registered_workers': allocation['total_workers'],
        'full_registered_judgments': allocation['total_judgments'],
    },
    'script_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
}
(OUT / 'evidence.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt['allocation_checks'], indent=2))

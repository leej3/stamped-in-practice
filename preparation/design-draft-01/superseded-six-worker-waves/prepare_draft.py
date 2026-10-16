"""Prepare a prospective allocation and exact-source draft artifacts; never launch."""
import collections
import hashlib
import json
from pathlib import Path
import secrets
import subprocess

ROOT = Path('/Users/johnlee/code/CON/stamped-in-practice')
OUT = Path(__file__).resolve().parent
STUDY = ROOT / 'studies/narps'
PIN = 'c7a135f92f92df15c379f7c2d9231f13981d76e4'
CONDITIONS = ['baseline', 'discover-general', 'discover-science', 'stamped-explicit']

def sha(b):
    return hashlib.sha256(b).hexdigest()

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

seedfile = OUT / 'allocation-seed.txt'
if not seedfile.exists():
    seedfile.write_text(secrets.token_hex(32) + '\n')
seed = seedfile.read_text().strip()
def rank(*parts):
    return sha((seed + '\n' + '\n'.join(map(str, parts))).encode())

# Each condition has multiplicities 2, 2, 1, 1 across four waves.
template = [[2,2,1,1], [1,1,2,2], [2,1,2,1], [1,2,1,2]]
rounds = []
for rnd in range(1,4):
    label_order = sorted(CONDITIONS, key=lambda c:rank(rnd, 'labels', c))
    wave_order = sorted(range(4), key=lambda w:rank(rnd, 'waves', w))
    workers = []
    seen = collections.Counter()
    ordinal = 0
    for wave, t in enumerate(wave_order, 1):
        members = [(c, occurrence) for col,c in enumerate(label_order)
                   for occurrence in range(template[t][col])]
        members.sort(key=lambda item:rank(rnd, wave, 'launch', *item))
        for position,(condition,_) in enumerate(members,1):
            ordinal += 1
            seen[condition] += 1
            workers.append({'run':f'narps-neutral-r{rnd}-{ordinal:02d}',
                            'condition':condition, 'replicate':seen[condition],
                            'wave':wave, 'launch_position':position})
    duplicates = []
    for condition in CONDITIONS:
        members = [w['run'] for w in workers if w['condition']==condition]
        duplicates.extend(sorted(members,key=lambda r:rank(rnd,'duplicate',r))[:2])
    judgments = [{'judgment':w['run']+'-j01','run':w['run'],'role':'primary'} for w in workers]
    judgments += [{'judgment':run+'-j02','run':run,'role':'duplicate'} for run in duplicates]
    judgments.sort(key=lambda j:rank(rnd,'judge-order',j['judgment']))
    for position,j in enumerate(judgments,1):
        j['dispatch_order']=position
    assert seen == dict.fromkeys(CONDITIONS,6)
    assert len(duplicates)==8 and len(set(duplicates))==8
    assert len(judgments)==32
    rounds.append({'round':rnd,'research_guidance_pin':None,
                   'final_untuned_evaluation':rnd==3,
                   'launch_order':workers,'duplicate_judgments':duplicates,
                   'judgment_dispatch_order':judgments})
save('allocation.json',{'schema_version':1,'status':'draft, not sealed or launched',
    'comparison_id':'narps-neutral-v1','randomization':{'seed_hex':seed,
    'method':'SHA256 sort keys with explicit newline-separated labels; see prepare_draft.py',
    'wave_count_template':template},'conditions':CONDITIONS,'rounds':rounds,
    'total_workers':72,'total_primary_judgments':72,'total_duplicate_judgments':24,
    'total_judgments':96,'primary_rule':'j01 is assigned primary before launch regardless of completion order or outcome'})

# Copy the exact registered scientific task and assessor guidance from the input pin.
task = git(STUDY,'show',f'{PIN}:input/study-task.md')
guidance = git(STUDY,'show',f'{PIN}:coordinator-guidance/judging.md')
(OUT / 'scientific-task.md').write_bytes(task)
(OUT / 'scientific-judging.md').write_bytes(guidance)
(OUT / 'conditions.json').write_bytes((ROOT / 'conditions.json').read_bytes())
addition = '''\nCommon resources\n\nThe supplied input files are materialized under `input/` in your workspace.\n`common-resources.md` lists the available executables and reference access.\nChoose the tools, analysis methods and delivery organization appropriate to the scientific task.\nKeep task-specific installations and changes within your workspace, leaving shared configuration unchanged.\nWhen finished, identify the report, code and supporting results in your final response and state any remaining limitations.\n'''
(OUT / 'worker-common.md').write_bytes(task + addition.encode())

# Exact pinned inputs, including stable original annex keys and local byte verification.
sources = json.loads(git(STUDY,'show',f'{PIN}:input/sources.json'))
inputs = []
for entry in git(STUDY,'ls-tree','-rz',PIN,'--','input').split(b'\0'):
    if not entry:
        continue
    header,path = entry.split(b'\t',1)
    mode,kind,oid = header.decode().split()
    path=path.decode()
    content=git(STUDY,'cat-file','blob',oid)
    item={'path':path,'git_mode':mode,'git_blob':oid}
    if mode=='120000':
        item['annex_key']=content.decode().split('/')[-1]
        expected=sources['files'][path.removeprefix('input/')]
        item.update(bytes=expected['bytes'],sha256=expected['sha256'])
    else:
        item.update(bytes=len(content),sha256=sha(content))
    local=STUDY / path
    if local.is_file():
        materialized=local.read_bytes()
        item['local_materialized_bytes_verified']=(len(materialized)==item['bytes'] and sha(materialized)==item['sha256'])
    else:
        item['local_materialized_bytes_verified']=None
    inputs.append(item)
assert len(inputs)==58
assert not any(item['local_materialized_bytes_verified'] is False for item in inputs)
save('input-manifest.json',{'study_commit':PIN,
 'input_tree':git(STUDY,'rev-parse',PIN+':input').decode().strip(),
 'source_scope':'Original input commit, not later result registrations',
 'verification_scope':'Existing local materialized input bytes; no retrieval or execution-host readiness claim',
 'files':inputs})

source_paths=['AGENTS.md','prompt.md','judge-prompt.md','conditions.json','comparison-plan.md',
'iterations/narps-v1/procedure.json','iterations/narps-v1/allocation.json',
'iterations/narps-v1/synthesis/README.md','scripts/study_seed.py','scripts/research_conditions.py']
save('source-manifest.json',{'coordinator_commit':git(ROOT,'rev-parse','HEAD').decode().strip(),
 'sources':[{'path':str(ROOT/p),'bytes':len((ROOT/p).read_bytes()),'sha256':sha((ROOT/p).read_bytes())} for p in source_paths],
 'scientific_task_sha256':sha(task),'scientific_judging_sha256':sha(guidance),
 'source_use':'Original task, scientific guidance, conditions and allocation semantics; completed synthesis only for declared design limitations. No prior answers or judgments supplied in worker drafts.'})
print('Prepared 72 worker assignments, 96 judgments and 58 pinned input records; locally verified:', sum(item['local_materialized_bytes_verified'] is True for item in inputs))

"""Retain coordinator observations from exact stopped native event citations."""
from pathlib import Path
import datetime,hashlib,json
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
sha=lambda x:hashlib.sha256(x).hexdigest()
records={'06': ({'discovery': True,
         'installation': True,
         'loaded': True,
         'application': 'PDF entrypoint loaded; no PDF rendering or extraction observed',
         'source_repository': 'https://github.com/openai/skills',
         'source_revision': None,
         'catalog_count': 39,
         'notes': ['Listed the curated catalog, installed pdf into .codex/skills, and loaded its '
                   'instructions.',
                   'No PDF rendering/extraction command was observed after loading. Installation and '
                   'instruction loading alone do not establish completed PDF review or benefit.']},
        {'installer_loaded': [8], 'catalog': [10], 'installation': [12], 'entrypoint_loaded': [15]}),
 '21': ({'discovery': False,
         'installation': False,
         'loaded': True,
         'application': 'supplied loop, conventions and validation instructions loaded',
         'source_repository': 'https://github.com/con/skills',
         'source_revision': 'f2e74ea3ed372f966c95692cb0826d56ad5e6a6c',
         'notes': ['Loaded the supplied loop, conventions and validation instructions.',
                   'Attempted a nonexistent loop references/stacks/python.md with stderr suppressed and true '
                   'fallback; its combined exit0 does not establish a successful read. Later enumerated the '
                   'real references directory.',
                   'No worker installation observed. Availability of supplied targets and procedural reads '
                   'are not causal benefit.']},
        {'loop_loaded': [6],
         'conventions_validation_loaded': [8],
         'missing_stack_reference_attempt': [10],
         'references_listed': [54]}),
 '04': ({'discovery': True,
         'installation': True,
         'loaded': True,
         'application': 'notebook entrypoint loaded; no scaffold or notebook execution observed',
         'source_repository': 'https://github.com/openai/skills',
         'source_revision': None,
         'catalog_count': 39,
         'notes': ['Listed curated skills, installed jupyter-notebook into .codex/skills and read the '
                   'entrypoint.',
                   'No notebook scaffold or notebook execution was observed; the visible file changes '
                   'concern a Python script and reports. Do not equate installation or reading with '
                   'completed notebook application.']},
        {'installer_loaded': [9], 'catalog': [13], 'installation': [16], 'entrypoint_loaded': [19]})}
for num,(observations,selections) in records.items():
 name='narps-neutral-r1-'+num;n=B/'runs'/name/'attempt-01/native';path=B/'runs'/name/'retention/skill-use-observations.json';assert not path.exists()
 source=n/'events.jsonl';raw=source.read_bytes();lines=raw.splitlines(keepends=True);events=[json.loads(x) for x in lines]
 assert any(e['type']=='turn.completed' for e in events)
 ev={k:[{'line':i,'item_id':events[i-1].get('item',{}).get('id'),'event_sha256':sha(lines[i-1].rstrip(b'\n')),'event':events[i-1]} for i in values] for k,values in selections.items()}
 sources=[]
 for filename in ['events.jsonl','launch.json','result.json','worker-end-state.json','skill-observations.json','condition-assignment.json','prompt-preflight.json']:
  p=n/filename;d=p.read_bytes();sources.append({'path':str(p),'sha256':sha(d),'bytes':len(d)})
 o={'schema_version':1,'kind':'coordinator-skill-use-observations','run_id':name,'extracted_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'assigned_condition':json.loads((n/'launch.json').read_text())['condition'],'scope':{'scientific_adequacy_assessed':False,'causal_effect_assessed':False,'worker_files_modified':False,'native_stream_line_count':len(lines),'complete_turn_observed':True,'limitation':'Availability is not use; observed procedural action is not causal benefit. Per-install duration is not inferred from reduced events.'},'observations':observations,'evidence':ev,'sources':sources}
 path.write_text(json.dumps(o,indent=2)+'\n');assert source.read_bytes()==raw
 print(name,sha(path.read_bytes()))

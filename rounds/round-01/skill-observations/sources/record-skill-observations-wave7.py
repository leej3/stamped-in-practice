"""Retain coordinator observations from exact stopped native event citations."""
from pathlib import Path
import datetime,hashlib,json
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
sha=lambda x:hashlib.sha256(x).hexdigest()
records={'24': ({'discovery': False,
         'installation': False,
         'loaded': True,
         'application': 'supplied loop, conventions, validation and project-creation instructions loaded',
         'source_repository': 'https://github.com/con/skills',
         'source_revision': 'f2e74ea3ed372f966c95692cb0826d56ad5e6a6c',
         'notes': ['Loaded the loop, validation and conventions; later loaded create-stamped-project and '
                   'principles/project-kind references.',
                   'Attempted a nonexistent stacks/python.md reference, then later enumerated the actual '
                   'stacks directory. Supplied target bytes are separately retained; instruction reads do '
                   'not establish causal benefit.']},
        {'loop_loaded': [6],
         'validation_conventions_loaded': [8],
         'missing_stack_reference': [10],
         'project_creation_loaded': [87],
         'principles_and_reference_listing': [89]}),
 '19': ({'discovery': True,
         'installation': True,
         'loaded': True,
         'application': 'PDF extraction attempted but download failed; notebook instructions loaded and '
                        'runtime availability checked',
         'source_repository': 'https://github.com/openai/skills',
         'source_revision': None,
         'catalog_count': 39,
         'notes': ['The initial repeated --path command installed only jupyter-notebook; a directory check '
                   'then a separate command installed pdf. Exact captured skill directories are indexed '
                   'separately.',
                   'Both entrypoints were loaded. PDF download returned HTTP522/exit22 before the &&-linked '
                   'pdftotext command could run.',
                   'No notebook scaffold or notebook execution was observed. The common interpreter lacked '
                   'nbformat, nbclient and jupyter in the recorded check. Availability and reading are not '
                   'completed application or causal benefit.']},
        {'installer_and_creator_loaded': [13],
         'catalog': [15],
         'initial_installation': [17],
         'installation_check': [19],
         'pdf_installation': [21],
         'entrypoints_loaded': [24],
         'pdf_attempt_failed': [30],
         'notebook_files_and_runtime_checked': [83, 85]}),
 '16': ({'discovery': False,
         'installation': False,
         'loaded': False,
         'application': 'no skill discovery, installation, load or application observed',
         'notes': ['The complete reduced native event stream contains no observed research-skill use; '
                   'runtime skill availability is recorded separately.']},
        {})}
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

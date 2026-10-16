"""Map exact extracted references to published retained objects; verify every byte."""
from pathlib import Path
import json,hashlib,os
repo=Path('/Users/johnlee/code/CON/stamped-in-practice');state=Path.home()/'.local/state/stamped-in-practice/narps-v1';out=repo/'iterations/narps-v1/synthesis';workers=Path('/Users/johnlee/code/CON/stamped-in-practice-workers/codex');mapped=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def walk(value):
 if isinstance(value,dict):
  if isinstance(value.get('path'),str) and 'sha256' in value:
   old=Path(value['path']);new=old
   if old.is_relative_to(state):
    parts=old.relative_to(state).parts;assert parts[0].startswith('narps-r1-'),str(old);new=repo/'studies/narps/results'/parts[0]/'coordinator/retention-01/indexable'/Path(*parts[1:])
   elif old.is_relative_to(workers):new=repo/'studies/narps/results'/old.relative_to(workers)
   elif not old.is_relative_to(repo):raise ValueError(str(old))
   assert new.is_file(),str(new);assert sha(new)==value['sha256'],str(new);mapped.append({'original':str(old),'published':str(new.relative_to(repo)),'sha256':value['sha256']});value={**value,'path':os.path.relpath(new,out)}
  return {k:walk(v) for k,v in value.items()}
 if isinstance(value,list):return [walk(v) for v in value]
 return value
index=walk(json.loads((state/'extraction-05/index.json').read_text()))
retained={x['run']:x['retention_commit'] for x in json.loads((repo/'studies/narps/retention-publications.json').read_text())['records']}
for row in index['runs']:row['retention_commit']=retained[row['run_id']]
(out/'index.json').write_text(json.dumps(index,indent=2)+'\n')
(out/'disposition.json').write_text(json.dumps(walk(json.loads((repo/'iterations/narps-v1/measurement-disposition-01.json').read_text())),indent=2)+'\n')
for name in ['reported-scientific-estimates.json','scientific-method-excerpts.json']:
 p=out/name;p.write_text(json.dumps(walk(json.loads(p.read_text())),indent=2)+'\n')
(out/'path-mapping.json').write_text(json.dumps({'scope':'Paths change; cited byte hashes and scientific identities do not. Raw output bindings retain historical paths.','records':mapped},indent=2)+'\n')
(out/'portable_index.py').write_bytes(Path(__file__).read_bytes())
print('verified references',len(mapped))

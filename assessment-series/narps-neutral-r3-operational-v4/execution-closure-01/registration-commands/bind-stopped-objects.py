"""Ordinary round-three identity bindings; no inspection or changes to outcomes."""
from pathlib import Path
import hashlib,json
G=Path(__file__).resolve().parent;B=G.parent
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
allocation=read(G/'original-allocation.json')
round3=next(r for r in allocation['rounds'] if r['round']==3)
assert len(round3['launch_order'])==24
assert all((B/f'round-03-wave-{w:02d}/stop-validation.json').exists() for w in range(1,9))
sources=[];objects=[]
for assignment in round3['launch_order']:
 run=assignment['run'];a=B/'runs'/run/'attempt-01';n=a/'native'
 assert read(B/'runs'/run/'dispatch.json')['status']=='launcher-finished'
 paths={'input_boundary':a/'input-boundary.json','worker_stop':n/'worker-end-state.json','delivery_capture':n/'original-delivery/manifest.json','native_result':n/'result.json'}
 row={'run':run,**{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()}}
 seed=read(paths['input_boundary']);stop=read(paths['worker_stop'])
 assert seed['run']==run
 assert stop['capture']['sha256']==row['delivery_capture']['sha256']
 sources.append(row);objects.append({'run':run,'seed_commit':seed['seed_commit'],'result_commit':stop.get('head_commit'),'worker_end_state_sha256':row['worker_stop']['sha256'],'delivery_capture_sha256':row['delivery_capture']['sha256']})
for name,value in [('original-object-sources.json',sources),('retained-objects.json',objects)]:
 with (G/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'workers':len(objects),'source_bindings_sha256':sha(G/'original-object-sources.json'),'retained_objects_sha256':sha(G/'retained-objects.json')}))

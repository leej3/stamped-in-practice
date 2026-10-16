"""Validate stopped original captures without scientific interpretation or writes."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,'/Users/johnlee/code/CON/stamped-in-practice/scripts')
from delivery_snapshot import validate_capture
b=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
rn,wn=map(int,sys.argv[1:]);w=b/f'round-{rn:02d}-wave-{wn:02d}';out=w/'stop-validation.json'
assert not out.exists();assert (w/'result.json').is_file()
rows=[]
for record in json.loads((w/'dispatch.json').read_text())['records']:
 name=record['assignment']['run'];n=b/'runs'/name/'attempt-01/native'
 result=json.loads((n/'result.json').read_bytes());stop=json.loads((n/'worker-end-state.json').read_bytes())
 assert json.loads((b/'runs'/name/'dispatch.json').read_text())['status']=='launcher-finished'
 identity=validate_capture(n/'original-delivery/manifest.json',stop['capture']['sha256'])
 assert identity['commit']==stop.get('head_commit')
 rows.append({'run':name,**{k:result[k] for k in ['returncode','elapsed_seconds','finished_at','native_session_ids']},'worker_head':stop.get('head_commit'),'stop_sha256':hashlib.sha256((n/'worker-end-state.json').read_bytes()).hexdigest(),'capture_sha256':stop['capture']['sha256'],'validation':identity})
out.write_text(json.dumps({'runs':rows,'scope':'Read-only complete-delivery validation; no scientific grading or changes'},indent=2)+'\n')
print(json.dumps({'wave':wn,'runs':[{k:r[k] for k in ['run','returncode','elapsed_seconds','capture_sha256']} for r in rows]}))

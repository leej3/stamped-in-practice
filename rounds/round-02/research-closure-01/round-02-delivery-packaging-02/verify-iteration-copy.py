from pathlib import Path
import hashlib,json
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
D=B/'dataset';O=D/'rounds/round-02/research-closure-01/delivery-packages'
rows=[]
for p in sorted(O.glob('narps-neutral-r2-*')):
 index=json.loads((p/'index.json').read_bytes())
 for f in index['files']:
  q=p/f['path'];h=hashlib.sha256()
  with q.open('rb') as s:
   for c in iter(lambda:s.read(1048576),b''):h.update(c)
  assert h.hexdigest()==f['sha256'] and q.stat().st_size==f['bytes']
 a=p/'delivery.tar.gz';assert a.is_symlink()
 rows.append({'run':p.name,'files_verified':len(index['files']),'archive_key':a.resolve().name,'capture_sha256':index['capture_sha256']})
assert len(rows)==24
v={'verified':True,'packages':rows,'scope':'Local iteration copies match existing verified complete package indexes; no remote payload retrieval claimed.','remote_payload_status':'pending'}
(O/'copy-verification.json').write_text(json.dumps(v,indent=2)+'\n');print('24 local iteration package copies verified; remote payloads pending')

"""Archive a verified package including embedded Git stores; expose exact index inputs."""
import argparse,hashlib,json,tarfile,shutil,stat,os,datetime
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('package');p.add_argument('output');a=p.parse_args();src=Path(a.package);out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
manifest=json.loads((src/'package-manifest.json').read_text());assert manifest['status']=='verified'
archive=out/'package.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=6,dereference=False) as tar:
 for p in sorted(src.iterdir()):tar.add(p,arcname=p.name,recursive=True)
verified=[]
with tarfile.open(archive,'r:gz') as tar:
 members={m.name.rstrip('/'):m for m in tar.getmembers()}
 expected={x['package_path'] for x in manifest['files']}|{'evidence','package-manifest.json','package-plan.json','package_retention.py'};assert set(members)==expected,(set(members)-expected,expected-set(members))
 for row in manifest['files']:
  member=members[row['package_path']]
  if row['kind']=='file':
   assert member.isfile() or member.islnk();raw=tar.extractfile(member);h=hashlib.sha256();size=0
   for chunk in iter(lambda:raw.read(1024*1024),b''):h.update(chunk);size+=len(chunk)
   assert h.hexdigest()==row['sha256'] and size==row['size'];assert stat.S_IMODE(member.mode)==row['mode']
  elif row['kind']=='directory':assert member.isdir()
  elif row['kind']=='symlink':assert member.issym() and member.linkname==row.get('target',row.get('link_target'))
  else:raise ValueError(row)
 for name in ['package-manifest.json','package-plan.json','package_retention.py']:assert tar.extractfile(name).read()==(src/name).read_bytes()
selected=[]
for row in manifest['files']:
 rel=row['path'];path=Path(rel)
 if row['kind']!='file':continue
 keep=(rel.startswith('launch/native/') and path.name in ['launch.json','result.json','worker-end-state.json','procedure-status.json','prompt.txt','events.jsonl','final.txt','skill-observations.json','condition-assignment.json','prompt-preflight.json']) or (rel.startswith('judgment-') and '/native/' in rel and path.name in ['launch.json','result.json','procedure-status.json','prompt.txt','events.jsonl','final.txt']) or (rel.startswith('judgment-') and len(path.parts)==3 and path.parts[1]=='judgment' and (path.name.endswith('-assessment.md') or path.name.endswith('-response.json') or path.name.endswith('-fresh-rerun.json'))) or (rel.startswith('retention/') and path.name in ['environment-snapshot.json','worker-environment-snapshot.lock','skill-use-observations.json','result.json','result-complete.json'] and len(path.parts)<=3) or (rel.startswith('retention/') and path.name.endswith('-output-binding.json'))
 if not keep:continue
 source=src/row['package_path'];dest=out/'indexable'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);assert sha(dest)==row['sha256'];selected.append({'source_path':rel,'path':str(dest.relative_to(out)),'sha256':row['sha256']})
for name in ['package-manifest.json','package-plan.json','package_retention.py']:shutil.copyfile(src/name,out/name)
shutil.copyfile(__file__,out/'bundle_package.py')
receipt={'schema_version':1,'status':'verified','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package_manifest_sha256':sha(src/'package-manifest.json'),'archive':{'path':'package.tar.gz','bytes':archive.stat().st_size,'sha256':sha(archive),'verified_entries':len(manifest['files']),'scope':'Every package file, directory, symlink and embedded Git store retained; no extra exclusions.'},'indexable':selected,'scientific_result':manifest['scientific_object']['result_commit'],'source_package':str(src)};(out/'bundle-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'output':str(out),'archive':receipt['archive'],'indexable_files':len(selected)}))

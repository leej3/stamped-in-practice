from pathlib import Path
import sys,json,tarfile,gzip,os,shutil
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');R=B/'operational-synthesis-proof-package-01';src=B/'operational-synthesis-publication-01'
sys.path.insert(0,str(B/'operational-support-tools-01'))
import package as method
proof=json.loads((src/'git-publication-verification.json').read_text());assert proof['verified'] and proof['git_blobs_identical']
excluded=['fresh-git']
before=method.inventory(src,excluded)
(R/'manifest.json').write_text(json.dumps({'source':str(src),'prefix':'evidence/','exclusions':[{'path':'fresh-git','reason':'Independent Git recipient reconstructable at exact verified public commit; all received Git blobs verified against source, no Hub payloads fetched','proof_sha256':method.sha(src/'git-publication-verification.json'),'commit':proof['commit']}],'entries':before},indent=2)+'\n')
a=R/'evidence.tar.gz'
with a.open('xb') as f,gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0,compresslevel=6) as z,tarfile.open(fileobj=z,mode='w|',format=tarfile.PAX_FORMAT) as tf:
 for r in before:
  m=tarfile.TarInfo('evidence/'+r['path']);m.mode=r['mode'];m.uid=m.gid=m.mtime=0
  if r['kind']=='directory':m.type=tarfile.DIRTYPE;tf.addfile(m)
  elif r['kind']=='symlink':m.type=tarfile.SYMTYPE;m.linkname=r['target'];tf.addfile(m)
  else:
   m.size=r['bytes'];fd,name=method.safe._parent(src,r['path'])
   try:
    stream,meta=method.safe._file(fd,name)
    with stream:tf.addfile(m,stream);method.safe._stable(fd,name,meta,stream)
   finally:os.close(fd)
v=method.verify(a,before);assert method.inventory(src,excluded)==before
for p in [Path(__file__),Path(method.__file__),Path(method.safe.__file__)]:shutil.copy2(p,R/p.name)
v.update(source_unchanged=True,archive_sha256=method.sha(a),archive_bytes=a.stat().st_size,manifest_sha256=method.sha(R/'manifest.json'),publication_status='pending Hub transport recovery; not remotely verified')
(R/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))

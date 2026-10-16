from pathlib import Path
import sys,json,tarfile,gzip,os,shutil,hashlib
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');R=B/'reporting-relocation-package-01';src=B/'reporting-relocation-validation-01'
sys.path.insert(0,str(B/'operational-support-tools-01'))
import package as method
before=method.inventory(src,[])
(R/'manifest.json').write_text(json.dumps({'source':str(src),'prefix':'evidence/','exclusions':[],'entries':before},indent=2)+'\n')
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
v=method.verify(a,before);assert method.inventory(src,[])==before
for p in [Path(method.__file__),Path(method.safe.__file__)]:shutil.copy2(p,R/('method-'+p.name))
v.update(source_unchanged=True,archive_sha256=method.sha(a),archive_bytes=a.stat().st_size,manifest_sha256=method.sha(R/'manifest.json'),publication_status='pending Hub transport recovery; not remotely verified')
(R/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))

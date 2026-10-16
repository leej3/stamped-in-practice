"""Archive the exact closed preservation set; no scientific execution or edits."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,shutil,stat,tarfile
import package_delivery as safe

def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
 with p.open('x') as f:f.write(json.dumps(v,indent=2,sort_keys=True)+'\n')
def inventory(root,excluded):
 rows=[]
 def visit(p):
  rel=str(p.relative_to(root))
  if rel in excluded:return
  s=p.lstat();r={'path':rel,'mode':stat.S_IMODE(s.st_mode)}
  if stat.S_ISDIR(s.st_mode):
   r['kind']='directory';rows.append(r)
   for q in sorted(p.iterdir()):visit(q)
   return
  if stat.S_ISLNK(s.st_mode):r.update(kind='symlink',target=os.readlink(p),sha256=hashlib.sha256(os.fsencode(os.readlink(p))).hexdigest())
  elif stat.S_ISREG(s.st_mode):
   fd,name=safe._parent(root,rel)
   try:
    stream,meta=safe._file(fd,name)
    with stream:
     digest=safe._digest(stream);safe._stable(fd,name,meta,stream)
   finally:os.close(fd)
   r.update(kind='file',bytes=s.st_size,sha256=digest)
  else:raise ValueError('Unsupported entry '+rel)
  rows.append(r)
 for p in sorted(root.iterdir()):visit(p)
 return rows

def verify(archive,rows):
 expected={'evidence/'+r['path']:r for r in rows};seen=set();count=0
 with gzip.open(archive,'rb') as z,tarfile.open(fileobj=z,mode='r|',ignore_zeros=True) as tf:
  for m in tf:
   safe._relative(m.name);assert m.name not in seen and m.name in expected,m.name
   seen.add(m.name);r=expected[m.name];assert m.mode==r['mode'],m.name
   if r['kind']=='directory':assert m.isdir() and not m.size
   elif r['kind']=='symlink':assert m.issym() and m.linkname==r['target'] and not m.size
   else:
    assert m.isfile() and not m.islnk() and m.size==r['bytes'],m.name
    with tf.extractfile(m) as f:assert safe._digest(f)==r['sha256'],m.name
    count+=m.size
 assert seen==set(expected)
 return {'verified':True,'members':len(seen),'regular_file_bytes':count,'extracted':False,'checks':['exact member set','kinds','modes','streamed SHA256','literal links','gzip integrity']}

def main():
 a=argparse.ArgumentParser();a.add_argument('source',type=Path);a.add_argument('output',type=Path);args=a.parse_args();src=args.source;out=args.output
 out.mkdir(parents=True,exist_ok=False);idx=src/'completion-index.json';raw=idx.read_bytes();i=json.loads(raw)
 assert i['schema']=='operational-native-closed-slot-v1' and i['source_closed_for_coordinator']
 assert i['series_id']=='narps-neutral-r1-operational-v4' and i['assessment_procedure_sha256']=='6f25ebbec5310442e8fd3fd20bd20682ecb5653b350362119af3e825a2668084'
 excluded=[str(Path(r['path']).relative_to(src)) for r in i['excluded_caches']]
 assert sorted(excluded)==['native-publication-01/fresh-check-01','native-publication-01/proof-fresh-check-01','native-publication-01/publisher']
 before=inventory(src,excluded);expected=sorted(i['closed_files']+[{'path':'completion-index.json','kind':'file','mode':stat.S_IMODE(idx.stat().st_mode),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}],key=lambda r:r['path'])
 assert sorted(before,key=lambda r:r['path'])==expected,'Closed source changed or has unindexed entries'
 save(out/'member-manifest.json',{'prefix':'evidence/','source':str(src),'source_completion_index_sha256':sha(idx),'excluded_verified_caches':i['excluded_caches'],'entries':before})
 archive=out/'support.tar.gz'
 with archive.open('xb') as f,gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0,compresslevel=6) as z,tarfile.open(fileobj=z,mode='w|',format=tarfile.PAX_FORMAT) as tf:
  for r in before:
   m=tarfile.TarInfo('evidence/'+r['path']);m.mode=r['mode'];m.uid=m.gid=m.mtime=0
   if r['kind']=='directory':m.type=tarfile.DIRTYPE;tf.addfile(m)
   elif r['kind']=='symlink':m.type=tarfile.SYMTYPE;m.linkname=r['target'];tf.addfile(m)
   else:
    m.size=r['bytes'];fd,name=safe._parent(src,r['path'])
    try:
     stream,meta=safe._file(fd,name)
     with stream:tf.addfile(m,stream);safe._stable(fd,name,meta,stream)
    finally:os.close(fd)
 verification=verify(archive,before);after=inventory(src,excluded);assert before==after
 shutil.copy2(idx,out/'completion-index.json')
 for p in [Path(__file__),Path(safe.__file__)]:shutil.copy2(p,out/p.name)
 save(out/'package-verification.json',{**verification,'source_before_after_equal':True,'source_closed_index_exact':True,'slot':i['slot'],'series_id':i['series_id'],'native_publication_base':i['proof_commit'],'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'manifest_sha256':sha(out/'member-manifest.json'),'closed_index_sha256':sha(idx),'omissions':'Only the three independently verified publisher/recipient caches listed in the closed source index; all closed scientific and execution evidence retained.'})
 print(json.dumps(json.loads((out/'package-verification.json').read_text())))
if __name__=='__main__':main()

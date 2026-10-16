"""Check retained access proof and current scientific resources; launch no model."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,types,datetime
BASE=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
COORDINATOR=Path('/Users/johnlee/code/CON/stamped-in-practice')
RESOURCES=BASE/'dataset/resources'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def require(value,message):
 if not value: raise RuntimeError(message)
def verify_manifest(root,manifest):
 for item in manifest['files']:
  p=root/item['path'];require(p.is_file(),str(p)+' missing')
  require(sha(p)==item['sha256'],str(p)+' hash mismatch')
  if 'bytes' in item: require(p.stat().st_size==item['bytes'],str(p)+' size mismatch')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('check',choices=['native-capture','annex-preservation','scientific-resources']);args=parser.parse_args()
 output=Path(os.environ['READINESS_ARTIFACT_DIR']);output.mkdir(parents=True,exist_ok=True)
 result={'check':args.check,'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_model_trial':False,'new_cluster_command':False}
 if args.check=='native-capture':
  root=RESOURCES/'native-host-preflight-01';verify_manifest(root,read(root/'manifest.json'))
  previous=read(root/'runtime-profile.json');access=read(root/'capture-access.json')
  require(all(access.get(k) is True for k in ['hosted_metadata_received','checkpoint_matches','session_matches','remote_checkpoint_matches']),'retained capture proof incomplete')
  sys.path.insert(0,str(COORDINATOR/'scripts'));import assessment_procedure
  cfg=read(Path.home()/'.config/stamped-in-practice/launch.json')
  identity=assessment_procedure.host_identity(types.SimpleNamespace(**cfg))
  require(identity==previous['host_identity'],'runtime/profile changed since retained access check')
  result.update(current_identity=identity,retained_access=access,scope='Current runtime/profile hashes plus retained recent hosted read; no new capture or model request')
 elif args.check=='annex-preservation':
  root=RESOURCES/'annex-publication-reference';verify_manifest(root,read(root/'reference.json'))
  proof=read(root/'result-complete.json');require(proof['success'] is True and proof['annex_paths']==42 and proof['proof_files_verified']==400,'incomplete independent retrieval proof')
  result.update(retained_proof=proof,reference=read(root/'reference.json'),scope='Exact preserved independent upload/retrieval evidence; no new artifact or remote transfer is claimed by this check')
 else:
  inventory=read(RESOURCES/'input-manifest.json');verified=[]
  for item in inventory['files']:
   p=COORDINATOR/'studies/narps'/item['path'];require(p.is_file(),item['path']+' unavailable')
   require(p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],item['path']+' differs')
   verified.append({'path':item['path'],'sha256':item['sha256'],'bytes':item['bytes']})
  env=BASE/'common-environment';expected=read(RESOURCES/'common-environment/inventory.json')
  require(sha(env/'pixi.toml')==expected['manifest_sha256'],'resource manifest changed')
  require(sha(env/'pixi.lock')==expected['lock_sha256'],'resource lock changed')
  code="import json,importlib.metadata as m;print(json.dumps({n:m.version(n) for n in ['numpy','scipy','pandas','matplotlib','nibabel','nilearn','datalad','con-duct']}))"
  command=[str(env/'.pixi/envs/default/bin/python'),'-c',code];r=subprocess.run(command,capture_output=True,text=True,check=True)
  require(json.loads(r.stdout)==expected['versions']['packages'],'resource package versions changed')
  result.update(inputs=verified,environment_manifest_sha256=expected['manifest_sha256'],environment_lock_sha256=expected['lock_sha256'],package_check={'argv':command,'stdout':r.stdout,'stderr':r.stderr,'returncode':r.returncode},scope='Current materialized input bytes, declared resource files and package imports; no scientific analysis executed')
 result['success']=True
 (output/'verification.json').write_text(json.dumps(result,indent=2)+'\n');shutil.copy2(__file__,output/'probe.py')
 print(json.dumps({'check':args.check,'success':True,'scope':result['scope']}))
if __name__=='__main__': main()

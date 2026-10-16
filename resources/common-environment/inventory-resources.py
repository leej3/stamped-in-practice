from pathlib import Path
import json,hashlib,subprocess,shutil,resource,datetime,os
root=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment')
records=[]
def run(argv):
 r=subprocess.run(argv,capture_output=True,text=True)
 records.append({'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 r.check_returncode();return r.stdout
packages=json.loads(run(['pixi','list','--manifest-path',str(root/'pixi.toml'),'--json']))
interpreter=root/'.pixi/envs/default/bin/python'
versions=json.loads(run([str(interpreter),'-c',"import json,sys,importlib.metadata as m;print(json.dumps({'python':sys.version,'executable':sys.executable,'packages':{n:m.version(n) for n in ['numpy','scipy','pandas','matplotlib','nibabel','nilearn','datalad','con-duct']}}))"]))
hardware={k:run(['sysctl','-n',k]).strip() for k in ['hw.memsize','hw.physicalcpu','hw.logicalcpu']}
state={'schema_version':1,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'attribution':'Optional coordinator-provided common environment; not worker-created environment evidence','manifest_sha256':hashlib.sha256((root/'pixi.toml').read_bytes()).hexdigest(),'lock_sha256':hashlib.sha256((root/'pixi.lock').read_bytes()).hexdigest(),'versions':versions,'all_packages':packages,'hardware':hardware,'concurrency':3,'resource_limits':{k:list(resource.getrlimit(getattr(resource,k))) for k in ['RLIMIT_CPU','RLIMIT_AS','RLIMIT_DATA','RLIMIT_NPROC','RLIMIT_NOFILE']},'free_disk_bytes':shutil.disk_usage(root).free,'limits_scope':'Current coordinator process and host values; no separately enforced per-worker CPU or memory quota. Three native sessions share this host.','thread_environment':{k:'1' for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']},'isolation_limit':'Separate worker repositories, session profiles and selected caches do not enforce same-user filesystem containment. Shared common environment is designated read-only by instructions, not a separate OS identity.'}
(root/'inventory.json').write_text(json.dumps(state,indent=2)+'\n')
(root/'inventory-commands.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps({k:state[k] for k in ['manifest_sha256','lock_sha256','versions','hardware','resource_limits','free_disk_bytes']}))

"""Verify a lean public parent clone and selective nested payload retrieval."""
from pathlib import Path
import subprocess,json,os,hashlib,shutil
out=Path(__file__).parent/'parent-fresh-check-01';out.mkdir(exist_ok=False)
shutil.copyfile(__file__,out/'verification.py')
repo=out/'recipient';records=[]
px=['pixi','run','--locked','--manifest-path','/Users/johnlee/code/CON/stamped-in-practice/pixi.toml']
def run(argv):
 p=subprocess.run(argv,cwd=out,capture_output=True,text=True,env=dict(os.environ,GIT_TERMINAL_PROMPT='0'),timeout=600)
 i=len(records)+1
 for k,v in [('stdout',p.stdout),('stderr',p.stderr)]:(out/f'{i:03d}.{k}').write_text(v)
 records.append(dict(argv=argv,returncode=p.returncode,stdout=f'{i:03d}.stdout',stderr=f'{i:03d}.stderr'))
 (out/'commands.json').write_text(json.dumps(records,indent=2)+'\n');p.check_returncode();return p.stdout
def git(r,*a):return run(['git','-C',str(r),*a])
def annex(r,*a):return run(px+['git','-C',str(r),'annex',*a])
def route(r):
 git(r,'fetch','--no-tags','origin','git-annex:refs/remotes/origin/git-annex')
 git(r,'config','remote.origin.annex-ignore','true');annex(r,'init','lean migration retrieval proof')
 git(r,'remote','add','con-hub','https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git')
 git(r,'config','remote.con-hub.annexurl','annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp');annex(r,'merge')
def selected_payload(r,path):
 key=annex(r,'lookupkey','--',path).strip();assert key.startswith('SHA256E-')
 assert not (r/path).exists()
 annex(r,'get','--from','con-hub','--',path)
 digest=hashlib.sha256((r/path).read_bytes()).hexdigest();assert digest==key.split('--')[1].split('.')[0]
 return dict(path=path,key=key,sha256=digest,bytes=(r/path).stat().st_size)
result=dict(success=False,parent_commit='e8ff6ec4eee2252e3331c04586d0803cd0ca2d2c',
 dataset_commit='14e22eada5f5af9db83f734ff291298441c3f1f2',scope='Public HTTPS Git clone; authorized same-host con-hub content retrieval.')
try:
 run(['git','clone','--depth','1','--single-branch','--branch','main','https://github.com/leej3/stamped-in-practice.git',str(repo)])
 assert git(repo,'rev-parse','HEAD').strip()==result['parent_commit']
 initial=git(repo,'submodule','status').splitlines();assert len(initial)==4 and all(x.startswith('-') for x in initial)
 result['initial_four_root_submodules_uninitialized']=True
 git(repo,'submodule','update','--init','--depth','1','--','iterations/narps-v1')
 it=repo/'iterations/narps-v1';assert git(it,'rev-parse','HEAD').strip()==result['dataset_commit']
 assert (it/'DATASET.md').is_file()
 assert all(x.startswith('-') for x in git(it,'submodule','status').splitlines())
 route(it)
 result['selected_figure']=selected_payload(it,'synthesis/figures/checklist-evidence.png')
 git(it,'submodule','update','--init','--depth','1','--','study')
 study=it/'study';initial_results=git(study,'submodule','status').splitlines();assert len(initial_results)==12 and all(x.startswith('-') for x in initial_results)
 git(study,'submodule','update','--init','--depth','1','--','results/narps-r1-01')
 exp=study/'results/narps-r1-01';route(exp)
 paths=[line.split('\t',1)[1] for line in git(exp,'ls-tree','-r','HEAD').splitlines() if line.startswith('120000 ') and '\tresults/' in line]
 chosen=next(x for x in paths if x.endswith('.png'))
 result['selected_scientific_payload']=selected_payload(exp,chosen)
 states=git(study,'submodule','status').splitlines();assert sum(x.startswith('-') for x in states)==11
 assert not (it/'assessment/.git').exists() and not (repo/'studies/narps/.git').exists()
 result.update(success=True,remaining_experiments_uninitialized=11,root_study_and_assessors_uninitialized=True,
               iteration_dataset_id=git(it,'config','--file','.datalad/config','--get','datalad.dataset.id').strip())
except Exception as e:result['error']=f'{type(e).__name__}: {e}'
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
raise SystemExit(0 if result['success'] else 1)

from pathlib import Path
import subprocess,json,hashlib,shutil
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');D=B/'dataset';M=Path('/Users/johnlee/code/CON/stamped-in-practice');R=B/'round-01-synthesis-01';PIXI=['pixi','run','--manifest-path',str(M/'pixi.toml'),'--locked'];commands=[]
host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_bytes())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def run(argv,cwd=D,allow=False):
 argv=list(map(str,argv));p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True);commands.append({'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});save(R/'publish-commands.json',commands)
 if not allow:p.check_returncode()
 return p if allow else p.stdout.strip()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
old=run(['git','rev-parse','HEAD']);assert old=='0fabf08'+old[7:]
assert run(['git','remote','get-url','--push','origin'])=='git@github.com:leej3/stamped-in-practice.git'
run(PIXI+['git','add','--','README.md','STATUS.md','progress.json','rounds'])
authored=['README.md','STATUS.md','rounds/round-01/synthesis/README.md','rounds/round-01/synthesis/viability.md','rounds/round-01/synthesis/REPRODUCE.md','rounds/round-01/synthesis/EXPERIMENTS.md']
run(['git','diff','--cached','--check','--',*authored])
full=run(['git','diff','--cached','--check'],allow=True);save(R/'raw-evidence-whitespace.json',{'returncode':full.returncode,'scope':'Historical captured report/record whitespace is preserved; authored prose checked separately.','stdout':full.stdout,'stderr':full.stderr})
changed=run(['git','diff','--cached','--name-only']).splitlines();assert all(p in authored or p=='progress.json' or p.startswith('rounds/') for p in changed)
files=[{'path':p,'bytes':(D/p).stat().st_size,'sha256':sha(D/p)} for p in changed];save(R/'publication-files.json',files)
tr=run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh']);msg=R/'message.txt';msg.write_text('docs(results): close the first neutral comparison round\n\nRetain all 24 original deliveries and 32 assigned assessments. Report\n11 metadata-related exclusions separately from scientific outcomes,\nwith reproducible tables, figures and the prospective boundary decision.\n\n'+tr+'\n');run(['git','commit','-F',msg]);head=run(['git','rev-parse','HEAD'])
for p in ['allocation.json','procedure.json','registration.json','registration.md','.gitattributes']:
 assert run(['git','rev-parse',head+':'+p])==run(['git','rev-parse',old+':'+p]),p
found=[json.loads(s) for s in run(PIXI+['git','annex','find','--json']).splitlines() if s];annex=[r for r in found if r['file'] in changed];paths=[r['file'] for r in annex];save(R/'annex-files.json',annex)
if paths:run(PIXI+['git','annex','copy','--to',host['annex_remote'],'--',*paths])
run(['git','push','origin','HEAD:refs/heads/codex/iteration-narps-neutral-v1'])
for attempt in range(3):
 run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex']);run(PIXI+['git','annex','merge']);p=run(['git','push','origin','git-annex:git-annex'],allow=True)
 if not p.returncode:break
 if not(any(s in p.stderr for s in ['non-fast-forward','fetch first']) or ('cannot lock ref' in p.stderr and 'refs/heads/git-annex' in p.stderr and 'but expected' in p.stderr)):p.check_returncode()
else:raise RuntimeError('annex push race did not settle')
rec=R/'fresh-recipient';rec.mkdir();run(['git','init','--initial-branch','received'],rec);run(['git','remote','add','origin','https://github.com/leej3/stamped-in-practice.git'],rec);run(['git','config','remote.origin.annex-ignore','true'],rec);run(['git','fetch','--no-tags','origin',head],rec);run(['git','checkout','--detach','FETCH_HEAD'],rec);assert not(rec/'.git/objects/info/alternates').exists()
for p in paths:assert not(rec/p).exists(),p
run(PIXI+['git','annex','init','independent round-one synthesis recipient'],rec);run(['git','remote','add',host['annex_remote'],host['annex_git_url']],rec);run(['git','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url']],rec);run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'],rec);run(PIXI+['git','annex','merge'],rec)
if paths:run(PIXI+['git','annex','get','--from',host['annex_remote'],'--',*paths],rec)
for r in files:assert sha(rec/r['path'])==r['sha256'] and (rec/r['path']).stat().st_size==r['bytes'],r['path']
assert run(['git','status','--porcelain'],rec)==''
for p in ['rounds/round-01/synthesis/attrition/assessment-attrition.png','rounds/round-01/synthesis/figures/scientific-adequacy.png']:
 assert run(['git','ls-tree','HEAD',p],rec).startswith('100644 ')
save(R/'publication-result.json',{'verified':True,'commit':head,'parent':old,'files_verified':len(files),'annex_payload_paths_freshly_retrieved':len(paths),'all_changed_payload_bytes_verified':True,'no_git_alternates':True,'frozen_records_unchanged':True,'figures_git_browsable':True,'recipient':str(rec)});print(head)

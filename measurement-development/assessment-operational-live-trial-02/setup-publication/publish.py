from pathlib import Path
import hashlib,json,subprocess,shutil
R=Path(__file__).resolve().parent;B=R.parent;M=Path('/Users/johnlee/code/CON/stamped-in-practice');S=Path('/Users/johnlee/.local/share/wt-utils/worktrees/1887/stamped-in-practice/studies/assessment-fixture')
H=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_bytes());PX=['pixi','run','--manifest-path',str(M/'pixi.toml'),'--locked'];URL='git@github.com:leej3/stamped-in-practice.git';READ='https://github.com/leej3/stamped-in-practice.git';commands=[]
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def run(a,cwd,allow=False):
 a=list(map(str,a));p=subprocess.run(a,cwd=cwd,capture_output=True,text=True);commands.append({'argv':a,'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});save(R/'commands.json',commands)
 if not allow:p.check_returncode()
 return p if allow else p.stdout.strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
refs=json.loads((R/'initial-refs.json').read_bytes());key=run(['git','show','3b263a0c58cc565d67e9092911086ecba4e8381e:input/paired-assay.csv'],S).split('/')[-1];source=S/'input/paired-assay.csv';before={'link':source.readlink().as_posix(),'bytes':source.stat().st_size,'sha256':sha(source)};save(R/'source-before.json',before)
P=R/'publisher';P.mkdir();run(['git','init','--initial-branch','preserve-fixture'],P);run(['git','remote','add','origin',READ],P);run(['git','remote','set-url','--push','origin',URL],P);run(['git','config','remote.origin.annex-ignore','true'],P);run(['git','fetch','--no-tags',str(S),refs[2]['expected']],P);run(['git','checkout','--detach','FETCH_HEAD'],P);run(PX+['git','annex','init','coordinator synthetic fixture publication'],P);run(['git','remote','add',H['annex_remote'],H['annex_git_url']],P);run(['git','config','remote.'+H['annex_remote']+'.annexurl',H['annex_url']],P)
spool=R/'payload-copy.csv';shutil.copyfile(source,spool);assert sha(spool)==before['sha256'];run(PX+['git','annex','setkey',key,str(spool)],P);run(PX+['git','annex','copy','--to',H['annex_remote'],'--','input/paired-assay.csv'],P)
for row in refs:
 repo=P if row['ref']=='codex/study-assessment-fixture' else M
 run(['git','remote','-v'],repo);run(['git','push',URL,row['expected']+':refs/heads/'+row['ref']],repo)
for attempt in range(5):
 run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'],P);run(PX+['git','annex','merge'],P);p=run(['git','push','origin','git-annex:git-annex'],P,True)
 if not p.returncode:break
 if not(any(s in p.stderr for s in ['non-fast-forward','fetch first']) or ('cannot lock ref' in p.stderr and 'refs/heads/git-annex' in p.stderr and 'but expected' in p.stderr)):p.check_returncode()
else:raise RuntimeError('annex race unresolved')
C=R/'fresh-recipient';C.mkdir();run(['git','init','--initial-branch','received'],C);run(['git','remote','add','origin',READ],C);run(['git','config','remote.origin.annex-ignore','true'],C)
for row in refs:
 run(['git','fetch','--no-tags','origin','refs/heads/'+row['ref']],C);assert run(['git','rev-parse','FETCH_HEAD'],C)==row['expected'];assert run(['git','cat-file','-t',row['expected']],C)=='commit'
run(['git','checkout','--detach',refs[2]['expected']],C);assert not(C/'.git/objects/info/alternates').exists();assert not(C/'input/paired-assay.csv').exists();run(PX+['git','annex','init','independent synthetic fixture recipient'],C);run(['git','remote','add',H['annex_remote'],H['annex_git_url']],C);run(['git','config','remote.'+H['annex_remote']+'.annexurl',H['annex_url']],C);run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'],C);run(PX+['git','annex','merge'],C);run(PX+['git','annex','get','--from',H['annex_remote'],'--','input/paired-assay.csv'],C);assert sha(C/'input/paired-assay.csv')==before['sha256']
for row in refs:assert run(['git','rev-parse',row['expected']+':studies/assessment-fixture'],C)==refs[2]['expected'] if row is not refs[2] else True
assert {'link':source.readlink().as_posix(),'bytes':source.stat().st_size,'sha256':sha(source)}==before
save(R/'result.json',{'verified':True,'refs':refs,'fixture_key':key,'fixture_payload':before,'fresh_empty_git_store':True,'no_alternates':True,'source_payload_unchanged':True,'setup_gitlinks_match_fixture':True,'no_fixture_merge_to_main':True});print('Published and independently retrieved three setup refs and exact fixture input.')

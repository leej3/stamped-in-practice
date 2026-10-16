from pathlib import Path
import subprocess,json,hashlib,datetime,sys
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');M=Path('/Users/johnlee/code/CON/stamped-in-practice');C=Path('/Users/johnlee/.local/share/wt-utils/worktrees/4af0/stamped-in-practice');R=B/'round-02-input-preparation-01';S=C/'studies/narps';P=['pixi','run','--manifest-path',str(M/'pixi.toml'),'--locked'];commands=[]
def run(a,cwd=C):
 p=subprocess.run(list(map(str,a)),cwd=cwd,text=True,capture_output=True);commands.append({'argv':list(map(str,a)),'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});(R/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');p.check_returncode();return p.stdout.strip()
assert run(['git','rev-parse','HEAD'])=='9068886f91615b2c69578bdaa6042a858f4d9011';assert run(['git','status','--porcelain'])==''
run(['git','submodule','update','--init','--depth','1','--','studies/narps'])
assert run(['git','rev-parse','HEAD'],S)=='221074f0ab291f0d2a0d919a2dd02e52a584f6b1'
run(P+['git','annex','init','round-two selected supplied inputs'],S)
run(['git','remote','add','supplied-input-cache',M/'studies/narps'],S)
run(P+['git','annex','get','--from','supplied-input-cache','--','input'],S)
sys.path.insert(0,str(C/'scripts'));import assessment_procedure as procedure
from study_seed import neutral_inputs
# Exports materialized inputs only to a temporary coordinator verification tree;
# no worker, seed commit, model session or scientific computation is created.
rows=neutral_inputs(S,'221074f0ab291f0d2a0d919a2dd02e52a584f6b1',R/'verified-input')
manifest=procedure.load_procedure(B/'dataset/procedure.json','b011f6e68dc6838e736f1ae2ad70d52896dab9b848d6f33950b4d35dd86b1521');procedure.check_sources(manifest,C,S,'9068886f91615b2c69578bdaa6042a858f4d9011')
assert run(['git','status','--porcelain'])==''
(R/'input-inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
result={'verified':True,'source_commit':'9068886f91615b2c69578bdaa6042a858f4d9011','study_commit':'221074f0ab291f0d2a0d919a2dd02e52a584f6b1','input_tree':run(['git','rev-parse','HEAD:input'],S),'materialized_files':len(rows),'annex_keys':len([r for r in rows if 'annex_key' in r]),'input_inventory_sha256':hashlib.sha256((R/'input-inventory.json').read_bytes()).hexdigest(),'retrieval_scope':'Existing verified local coordinator study input cache; no current Hub transfer success claimed.','full_original_working_source_guard_passed':True,'selected_study_only':True,'worker_or_native_launched':False,'candidate_status':run(['git','status','--porcelain']),'installed_submodules':run(['git','submodule','status'])}
(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

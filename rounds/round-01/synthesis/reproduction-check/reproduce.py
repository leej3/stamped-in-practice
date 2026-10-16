from pathlib import Path
import subprocess,json,hashlib,sys
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');D=B/'dataset';O=D/'rounds/round-01/synthesis';M=Path('/Users/johnlee/code/CON/stamped-in-practice');R=B/'round-01-synthesis-reproduction-01';R.mkdir();commands=[]
def run(argv):
 p=subprocess.run(list(map(str,argv)),cwd=M,capture_output=True,text=True);commands.append({'argv':list(map(str,argv)),'cwd':str(M),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});(R/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');return p
p=run(['pixi','run','--locked','python','scripts/aggregate_comparison.py','--allocation',D/'allocation.json','--index',O/'extraction/index.json','--output',R/'analysis','--assessor','assessment','--assessment-pin','assessment-version.json','--assessment-procedure-sha256','b011f6e68dc6838e736f1ae2ad70d52896dab9b848d6f33950b4d35dd86b1521']);assert p.returncode==2
checked=[]
for f in sorted((O/'extraction/analysis').glob('*.jsonl')):
 assert f.read_bytes()==(R/'analysis'/f.name).read_bytes(),f.name;checked.append({'path':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
sys.path.insert(0,str(M/'scripts'));from render_assessment_attrition import render
v=json.loads((O/'attrition/assessment-attrition.json').read_bytes());assert v['judgments_source_sha256']==hashlib.sha256((R/'analysis/judgments.jsonl').read_bytes()).hexdigest()
for row in v['rows']:
 for ref in row['evidence']:assert hashlib.sha256((O/'attrition'/ref['path']).read_bytes()).hexdigest()==ref['sha256']
(R/'attrition').mkdir();render(v['rows'],R/'attrition');assert (R/'attrition/assessment-attrition.png').read_bytes()==(O/'attrition/assessment-attrition.png').read_bytes()
result={'verified':True,'aggregate_exit':2,'expected_integrity_issues':11,'tables_byte_identical':checked,'attrition_png_byte_identical':True,'scope':'Reproduction from relocated retained extraction and hash-checked attrition table; no scientific replay or regrading.'};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

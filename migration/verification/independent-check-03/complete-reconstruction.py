"""Check relocated comparison tables, allowing only the declared path prefix."""
from pathlib import Path
import json
import hashlib
import shutil
import subprocess
base=Path(__file__).parent/'independent-check-03'
shutil.copyfile(__file__,base/'complete-reconstruction.py')
ds=base/'recipient'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result=json.loads((base/'result.json').read_text())
assert result['error']=='AssertionError: effort.jsonl'
result['initial_verification_limit']='The first comparison expected byte equality despite the declared evidence-path relocation. The original failed check is retained.'
del result['error']
tables=[]
for src in sorted((ds/'synthesis/aggregate').glob('*.jsonl')):
    dst=base/'aggregate'/src.name
    old=src.read_bytes();new=dst.read_bytes()
    expected=old.replace(b'../../../studies/narps/results/',b'../study/results/')
    assert new==expected,src.name
    tables.append(dict(path=src.name,old_sha256=sha(src),new_sha256=sha(dst),
                       byte_identical=old==new,only_declared_path_relocation=True))
assert len(tables)==18
assert (base/'aggregate/issues.jsonl').read_bytes()==b''
result['reconstructed_tables']=tables
result['all_outcomes_and_evidence_hashes_identical']=True
result['path_substitution']={'from':'../../../studies/narps/results/','to':'../study/results/'}
argv=['pixi','run','--locked','--manifest-path',str(ds/'synthesis/analysis/pixi.toml'),
      'python',str(ds/'synthesis/analysis/round1_figures.py'),'--tables',str(base/'aggregate'),
      '--estimates',str(ds/'replay/reported-scientific-estimates.json'),'--output',str(base/'figures')]
p=subprocess.run(argv,capture_output=True,text=True)
(base/'figures-command.json').write_text(json.dumps(dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr),indent=2)+'\n')
p.check_returncode()
pngs=[]
for src in sorted((ds/'synthesis/figures').glob('*.png')):
    dst=base/'figures'/src.name
    assert dst.read_bytes()==src.read_bytes(),src.name
    pngs.append(dict(path=src.name,sha256=sha(dst),byte_identical=True))
assert len(pngs)==4
result['reconstructed_figure_pngs']=pngs
result['success']=True
(base/'result-complete.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['reconstructed_tables','reconstructed_figure_pngs']},indent=2))

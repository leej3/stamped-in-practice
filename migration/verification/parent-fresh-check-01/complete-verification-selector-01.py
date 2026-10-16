from pathlib import Path
import subprocess,json,hashlib,shutil
base=Path(__file__).parent/'parent-fresh-check-01';shutil.copyfile(__file__,base/'complete-verification.py');r=base/'recipient';it=r/'iterations/narps-v1';s=it/'study';e=s/'results/narps-r1-01';rows=json.loads((base/'commands.json').read_text());px=['pixi','run','--locked','--manifest-path','/Users/johnlee/code/CON/stamped-in-practice/pixi.toml']
def run(argv):
 p=subprocess.run(argv,cwd=base,capture_output=True,text=True);i=len(rows)+1
 for suffix,data in [('stdout',p.stdout),('stderr',p.stderr)]:(base/f'{i:03d}.{suffix}').write_text(data)
 rows.append(dict(argv=argv,returncode=p.returncode,stdout=f'{i:03d}.stdout',stderr=f'{i:03d}.stderr'));(base/'commands-complete.json').write_text(json.dumps(rows,indent=2)+'\n');p.check_returncode();return p.stdout
inventory=[json.loads(x) for x in run(px+['git','-C',str(e),'annex','find','--anything','--json','--','results']).splitlines()]
chosen=next(x for x in inventory if x['file'].endswith('.png') and '/attempts/' not in x['file'])
assert not run(px+['git','-C',str(e),'annex','find','--in=here','--',chosen['file']]).strip()
run(px+['git','-C',str(e),'annex','get','--from','con-hub','--',chosen['file']]);p=e/chosen['file'];digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==chosen['key'].split('--')[1].split('.')[0]
states=run(['git','-C',str(s),'submodule','status']).splitlines();assert sum(x.startswith('-') for x in states)==11
assert not (it/'assessment/.git').exists() and not (r/'studies/narps/.git').exists()
result=json.loads((base/'result.json').read_text());assert result['error']=='StopIteration: ';del result['error'];result.update(success=True,initial_verification_limit='The first selector considered only symlink annex files; this source uses unlocked pointer files. Native annex inventory selects and validates both forms; original failure retained.',selected_scientific_payload=dict(path=chosen['file'],key=chosen['key'],sha256=digest,bytes=p.stat().st_size),remaining_experiments_uninitialized=11,root_study_and_assessors_uninitialized=True,iteration_dataset_id=run(['git','-C',str(it),'config','--file','.datalad/config','--get','datalad.dataset.id']).strip())
(base/'result-complete.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

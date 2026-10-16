"""Apply the reviewed structural replacement; retain original working directory."""
from pathlib import Path
import subprocess,json,shutil,hashlib
base=Path(__file__).parent
repo=Path('/Users/johnlee/code/CON/stamped-in-practice')
pin='14e22eada5f5af9db83f734ff291298441c3f1f2'
records=[]
def run(argv):
    p=subprocess.run(argv,cwd=repo,capture_output=True,text=True)
    records.append(dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
    (base/'parent-replacement-commands.json').write_text(json.dumps(records,indent=2)+'\n')
    p.check_returncode();return p.stdout
assert json.loads((base/'independent-check-03/result-complete.json').read_text())['success']
assert run(['git','rev-parse','HEAD']).strip()=='ffc236c5ad2946d93a2de327ec6833f800c3f7ac'
assert not run(['git','status','--porcelain']).strip()
assert not (base/'original-parent-directory').exists()
source=repo/'iterations/narps-v1'
run(['git','rm','-r','--cached','--','iterations/narps-v1'])
source.rename(base/'original-parent-directory')
modules=(base/'parent-replacement/.gitmodules').read_text().replace('git@github.com:leej3/stamped-in-practice.git','https://github.com/leej3/stamped-in-practice.git')
(repo/'.gitmodules').write_text(modules)
readme=(base/'parent-replacement/README.md').read_text().replace('](iterations/narps-v1/DATASET.md)',f'](https://github.com/leej3/stamped-in-practice/blob/{pin}/DATASET.md)')
(repo/'README.md').write_text(readme)
run(['snapper','-i','README.md'])
run(['git','add','.gitmodules','README.md'])
run(['git','update-index','--add','--cacheinfo',f'160000,{pin},iterations/narps-v1'])
run(['git','submodule','update','--init','--depth','1','--','iterations/narps-v1'])
run(['git','-C','iterations/narps-v1','remote','set-url','--push','origin','git@github.com:leej3/stamped-in-practice.git'])
assert run(['git','-C','iterations/narps-v1','rev-parse','HEAD']).strip()==pin
run(['git','diff','--cached','--check'])
patch=run(['git','diff','--cached','--binary']);(base/'parent-replacement-applied.patch').write_text(patch)
assert run(['git','diff','--name-only']).strip()==''
trailers=run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'])
message='refactor(research): register the completed iteration subdataset\n\nReplace the original iteration directory with its published DataLad pin.\nPreserve prefix history, all 711 original paths and 37 annex keys; keep\nthe full coordinator history on codex/narps-v1-before-migration.\n\nIndependent retrieval reconstructed all 18 comparison tables modulo the\ndeclared path relocation and reproduced four PNG figures byte for byte.\nStudy, result and assessor modules remain lazily selectable.\n\n'+trailers
(base/'parent-migration-commit.txt').write_text(message)
run(['git','commit','-F',str(base/'parent-migration-commit.txt')])
run(['git','push','origin','HEAD:refs/heads/main'])
print(run(['git','rev-parse','HEAD']))

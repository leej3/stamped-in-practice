"""Add clearly attributed navigation only when no original root README exists."""
from pathlib import Path
from urllib.parse import quote
import hashlib,json,shutil,subprocess,sys,traceback
root=Path(sys.argv[1]).resolve();repo=root/'publisher';prepared=json.loads((root/'prepared.json').read_text())
pixi=['pixi','run','--manifest-path','/Users/johnlee/code/CON/stamped-in-practice/pixi.toml','--locked'];commands=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def run(argv,allow=False):
    p=subprocess.run(list(map(str,argv)),cwd=repo,capture_output=True,text=True)
    commands.append({'argv':list(map(str,argv)),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    save(root/'commands-navigation.json',commands)
    if not allow:p.check_returncode()
    return p
try:
    assert not (root/'navigation.json').exists()
    assert run(['git','rev-parse','HEAD']).stdout.strip()==prepared['parent_commit']
    original_readme=any(e['published_path']=='README.md' for e in prepared['copied_files'])
    original_readme=original_readme or bool(run(['git','ls-tree','HEAD','README.md']).stdout.strip())
    evidence=repo/'coordinator/browsable-copy-01';paths=[]
    if not original_readme:
        assert not (repo/'README.md').exists() and not (repo/'README.md').is_symlink()
        files=[e['published_path'] for e in prepared['copied_files'] if e['kind']=='file' and not e['published_path'].startswith('.')]
        links=[p for p in files if Path(p).name.lower().startswith(('report','protocol')) or Path(p).suffix.lower() in {'.py','.r','.m','.sh','.ipynb','.png','.svg','.jpg','.jpeg','.webp'}]
        text='# '+prepared['run_id']+'\n\nCoordinator navigation for this stopped experiment. Original scientific files are copied unchanged from its captured delivery.\n\n'
        text+='\n'.join('- ['+p+']('+quote(p,safe='/')+')' for p in links)
        text+='\n\nThe [complete original archive](coordinator/delivery-01/delivery.tar.gz) remains authoritative. See the [copy manifest](coordinator/browsable-copy-01/manifest.json) for source hashes and storage, and [coordinator records](coordinator/README.md) for preservation provenance. This navigation adds no scientific execution or worker credit.\n'
        (repo/'README.md').write_text(text)
        cmd=pixi+['pre-commit','run','--config','/Users/johnlee/code/CON/stamped-in-practice/.pre-commit-config.yaml','snapper','--files','README.md']
        if run(cmd,allow=True).returncode:run(cmd)
        paths.append('README.md')
    if (root/'root-review-01.json').exists():
        dest=evidence/'review/root-review-01.json';dest.parent.mkdir();shutil.copy2(root/'root-review-01.json',dest)
        paths.append(str(dest.relative_to(repo)))
    shutil.copy2(Path(__file__),evidence/'add-navigation.py');paths.append('coordinator/browsable-copy-01/add-navigation.py')
    result={'coordinator_root_readme_added':not original_readme,'original_root_readme_preserved':bool(original_readme),
      'prepared_sha256':sha(root/'prepared.json'),'files':[{'path':p,'sha256':sha(repo/p)} for p in paths]}
    save(evidence/'navigation.json',result);paths.append('coordinator/browsable-copy-01/navigation.json')
    run(['git','add','--force','--',*paths]);run(['git','diff','--cached','--check','--','coordinator',*(['README.md'] if not original_readme else [])])
    result['navigation_manifest_sha256']=sha(evidence/'navigation.json');save(root/'navigation.json',result)
    (root/'prepared-with-navigation.patch').write_text(run(['git','diff','--cached','--binary']).stdout)
    (root/'prepared-with-navigation-stat.txt').write_text(run(['git','diff','--cached','--stat']).stdout)
    print(json.dumps({'root_navigation_added':not original_readme,'original_root_readme_preserved':bool(original_readme)}))
except BaseException:
    (root/'failure-navigation.txt').write_text(traceback.format_exc());raise

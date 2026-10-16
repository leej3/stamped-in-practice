"""Continue after preserving original atlas helper whitespace; never reformat it."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,traceback
root=Path(__file__).resolve().parent;repo=root/'publisher';cfg=json.loads((root/'config.json').read_text());commands=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def run(argv):
    p=subprocess.run(argv,cwd=repo,capture_output=True,text=True)
    commands.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    save(root/'commands-prepare-02.json',commands);p.check_returncode();return p.stdout
try:
    assert not (root/'prepared.json').exists() and (root/'failure-prepare.txt').exists()
    plan=json.loads(Path(cfg['plan_path']).read_text());capture=Path(plan['capture_manifest']['path'])
    assert sha(Path(cfg['plan_path']))==cfg['plan_sha256'] and sha(capture)==cfg['canonical']['capture_sha256']
    evidence=repo/'coordinator/browsable-copy-01';manifest=json.loads((evidence/'manifest.json').read_text())
    assert run(['git','rev-parse','HEAD']).strip()==cfg['canonical']['commit']==manifest['parent_commit']
    assert run(['git','rev-parse','HEAD:input']).strip()==manifest['input_tree']
    assert sha(repo/'coordinator/delivery-01/index.json')==cfg['canonical']['package_index_sha256']
    assert run(['git','diff','--cached','--name-only','--','input','coordinator/delivery-01','coordinator/original-manifest.json'])==''
    for e in manifest['copied_files']:
        path=e['published_path'];original=capture.parent/'content/workspace'/path
        assert sha(original)==sha(repo/path)==e['sha256']
        assert original.stat().st_size==(repo/path).stat().st_size==e['bytes']
        mode=run(['git','ls-files','--stage','--',path]).split()[0]
        assert mode==('120000' if e['storage']=='annex' else ('100755' if e['source_mode']&0o111 else '100644'))
    shutil.copy2(Path(__file__),evidence/'resume-prepare-02.py')
    save(evidence/'preserved-whitespace.json',{'path':'results/atlas/fsl/data/atlases/HarvardOxford/relabel',
      'meaning':'Original trailing whitespace is preserved exactly; formatting checks apply only to coordinator-authored changes.',
      'failed_check_log_sha256':sha(root/'commands-prepare.json'),'failure_receipt_sha256':sha(root/'failure-prepare.txt')})
    run(['git','add','--force','--','coordinator/browsable-copy-01/resume-prepare-02.py','coordinator/browsable-copy-01/preserved-whitespace.json'])
    run(['git','diff','--cached','--check','--','.gitattributes','coordinator'])
    (root/'prepared-diff-stat.txt').write_text(run(['git','diff','--cached','--stat']))
    (root/'prepared.patch').write_text(run(['git','diff','--cached','--binary']))
    save(root/'prepared.json',dict(manifest,publisher=str(repo),branch=cfg['branch'],
      annex_files=[e['published_path'] for e in manifest['copied_files'] if e['storage']=='annex'],
      package_index_sha256=cfg['canonical']['package_index_sha256'],plan_path=cfg['plan_path'],config_sha256=sha(root/'config.json'),
      retained_initial_failure='failure-prepare.txt',continuation='resume-prepare-02.py'))
    print(json.dumps({'prepared':True,'files':len(manifest['copied_files']),'annex_files':sum(e['storage']=='annex' for e in manifest['copied_files']),'original_whitespace_preserved':True}))
except BaseException:
    (root/'failure-prepare-02.txt').write_text(traceback.format_exc());raise

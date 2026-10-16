"""Fetch an exact presentation commit and verify only its new payloads."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,traceback
root=Path(sys.argv[1]).resolve();check=root/'fresh-check-01';check.mkdir();repo=check/'recipient';repo.mkdir()
pixi=['pixi','run','--manifest-path','/Users/johnlee/code/CON/stamped-in-practice/pixi.toml','--locked']
host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_text())
published=json.loads((root/'publication.json').read_text());prepared=json.loads((root/'prepared.json').read_text());commands=[]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def run(argv,_retry=False):
    p=subprocess.run(argv,cwd=repo,capture_output=True,text=True)
    commands.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    save(check/'commands.json',commands)
    if not _retry and p.returncode == 128 and 'ssh: connect to host github.com port 22: Operation timed out' in p.stderr and argv[:2] in [['git','fetch'],['git','ls-remote'],['git','push']]: return run(argv,True)
    p.check_returncode();return p.stdout.strip()
try:
    run(['git','init','--initial-branch','received'])
    run(['git','remote','add','origin','https://github.com/leej3/stamped-in-practice.git'])
    run(['git','config','remote.origin.annex-ignore','true'])
    run(['git','fetch','--no-tags','origin',published['commit']])
    run(['git','checkout','--detach','FETCH_HEAD'])
    assert not (repo/'.git/objects/info/alternates').exists()
    assert run(['git','rev-parse','HEAD'])==published['commit']
    run(['git','merge-base','--is-ancestor',prepared['parent_commit'],'HEAD'])
    assert run(['git','rev-parse','HEAD:input'])==prepared['input_tree']
    assert sha(repo/'coordinator/delivery-01/index.json')==prepared['package_index_sha256']
    assert sha(repo/'coordinator/original-manifest.json')==prepared['capture_sha256']
    assert run(['git','diff','--name-only',prepared['parent_commit'],'HEAD','--','input','coordinator/delivery-01','coordinator/original-manifest.json'])==''
    evidence=repo/'coordinator/browsable-copy-01'
    for name in ['manifest.json','plan.json','input-manifest.json','shared-input-route-proof.json','config.json','prepare.py']:
        assert sha(evidence/name)==sha(root/'publisher/coordinator/browsable-copy-01'/name)
    if (root/'navigation.json').exists():
        navigation=json.loads((root/'navigation.json').read_text())
        assert sha(evidence/'navigation.json')==navigation['navigation_manifest_sha256']
        for item in navigation['files']:assert sha(repo/item['path'])==item['sha256']
    if (root/'review-added.json').exists():
        for item in json.loads((root/'review-added.json').read_text())['files']:
            assert sha(repo/item['path'])==item['sha256']
    assert sha(evidence/'input-manifest.json')==prepared['shared_input_manifest_sha256']
    assert sha(evidence/'shared-input-route-proof.json')==prepared['shared_input_route_proof_sha256']
    route=json.loads((evidence/'shared-input-route-proof.json').read_text());inputs=json.loads((evidence/'input-manifest.json').read_text())
    assert route['verified'] and route['input_manifest_sha256']==prepared['shared_input_manifest_sha256']
    assert route['input_files_verified']==len(inputs['files'])==58 and inputs['input_tree']==prepared['input_tree']
    annex=[e for e in prepared['copied_files'] if e['storage']=='annex']
    absent={e['published_path']:not(repo/e['published_path']).exists() for e in annex};assert all(absent.values())
    run(pixi+['git','annex','init','independent browsable presentation receiver'])
    run(['git','remote','add',host['annex_remote'],host['annex_git_url']])
    run(['git','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url']])
    run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'])
    run(pixi+['git','annex','merge'])
    for e in annex:assert run(pixi+['git','annex','lookupkey',e['published_path']])==e['annex_key']
    if annex:run(pixi+['git','annex','get','--from',host['annex_remote'],'--',*[e['published_path'] for e in annex]])
    for e in prepared['copied_files']:
        path=repo/e['published_path'];mode=run(['git','ls-tree','HEAD','--',e['published_path']]).split()[0]
        expected='120000' if e['storage'] in ['annex','literal-link'] else ('100755' if e['source_mode']&0o111 else '100644')
        assert mode==expected
        if e['kind']=='file':assert sha(path)==e['sha256'] and path.stat().st_size==e['bytes']
        else:assert os.readlink(path)==e['target']
    assert run(['git','rev-parse','HEAD'])==published['commit'] and run(['git','status','--porcelain'])==''
    save(check/'result.json',{'verified':True,'commit':published['commit'],'input_tree':prepared['input_tree'],
      'copied_files_verified':len(prepared['copied_files']),'annex_files_absent_before_get':absent,
      'shared_input_route_proof_sha256':prepared['shared_input_route_proof_sha256'],
      'input_scope':'Exact input Git tree and manifest match the cited prior 58-payload retrieval; no repeated input download.',
      'original_archive_unchanged':True,'scientific_execution':False,'command_log_sha256':sha(check/'commands.json')})
    print(json.dumps({'verified':True,'commit':published['commit'],'files':len(prepared['copied_files'])}))
except BaseException:
    (check/'failure.txt').write_text(traceback.format_exc());raise

"""Prepare one reviewed browsable copy; only coordinator files are authored."""
from pathlib import Path, PurePosixPath
import hashlib, json, os, shutil, stat, subprocess, sys, traceback

config_path = Path(sys.argv[1]).resolve()
cfg = json.loads(config_path.read_text())
root = Path(cfg['root']); repo = root / 'publisher'; repo.mkdir()
main = Path('/Users/johnlee/code/CON/stamped-in-practice')
pixi = ['pixi', 'run', '--manifest-path', str(main/'pixi.toml'), '--locked']
host = json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_text())
canonical = cfg['canonical']; commands = []
assert cfg['run_id'] != 'narps-neutral-r1-20'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def save(path, value): path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')

def run(argv, allow=False):
    p = subprocess.run(list(map(str, argv)), cwd=repo, capture_output=True, text=True)
    commands.append({'argv':list(map(str, argv)), 'cwd':str(repo), 'returncode':p.returncode,
                     'stdout':p.stdout, 'stderr':p.stderr})
    save(root/'commands-prepare.json', commands)
    if not allow: p.check_returncode()
    return p

try:
    plan_path = Path(cfg['plan_path']); assert sha(plan_path) == cfg['plan_sha256']
    plan = json.loads(plan_path.read_text()); capture = Path(plan['capture_manifest']['path'])
    assert plan['run_id'] == cfg['run_id'] == canonical['run_id']
    assert sha(capture) == plan['capture_manifest']['sha256'] == canonical['capture_sha256']
    assert plan['original_worker_head'] == canonical['worker_head_commit']
    source_entries = {e['path']:e for e in json.loads(capture.read_text())['entries']}
    inputs_path = Path(cfg['input_manifest_path']); route_path = Path(cfg['input_route_proof_path'])
    assert sha(inputs_path) == cfg['input_manifest_sha256']
    assert sha(route_path) == cfg['input_route_proof_sha256']
    inputs = json.loads(inputs_path.read_text()); route = json.loads(route_path.read_text())
    assert route['verified'] and route['input_files_verified'] == len(inputs['files']) == 58
    assert route['input_manifest_sha256'] == cfg['input_manifest_sha256']
    assert inputs['input_tree'] == canonical['input_tree']
    run(['git','init','--initial-branch',cfg['branch']])
    run(['git','remote','add','origin','git@github.com:leej3/stamped-in-practice.git'])
    run(['git','config','remote.origin.annex-ignore','true'])
    run(['git','fetch','--no-tags','origin',canonical['commit']])
    run(['git','reset','--hard','FETCH_HEAD'])
    assert run(['git','rev-parse','HEAD']).stdout.strip() == canonical['commit']
    assert not (repo/'.git/objects/info/alternates').exists()
    assert run(['git','rev-parse','HEAD:input']).stdout.strip() == inputs['input_tree']
    assert run(['git','rev-parse',canonical['worker_head_commit']+':input']).stdout.strip() == inputs['input_tree']
    run(['git','merge-base','--is-ancestor',canonical['worker_head_commit'],'HEAD'])
    assert sha(repo/'coordinator/original-manifest.json') == canonical['capture_sha256']
    assert sha(repo/'coordinator/delivery-01/index.json') == canonical['package_index_sha256']
    archive_tree = run(['git','ls-tree','HEAD','coordinator/delivery-01/delivery.tar.gz']).stdout
    original_readme = run(['git','ls-tree','HEAD','README.md']).stdout
    run(pixi+['git','annex','init',cfg['run_id']+' browsable coordinator copy'])
    run(['git','remote','add',host['annex_remote'],host['annex_git_url']])
    run(['git','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url']])
    run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'])
    run(pixi+['git','annex','merge'])
    assert run(['git','rev-parse','HEAD']).stdout.strip() == canonical['commit']
    # Preflight the complete reviewed plan before copying any original files.
    for e in plan['entries']:
        path = PurePosixPath(e['path']); assert not path.is_absolute() and '..' not in path.parts
        assert not any(c in e['path'] for c in '\n\r\0*?[]'), 'Unreviewed attribute pattern'
        assert e['capture_path'] == 'content/workspace/'+e['path']
        source = source_entries[e['capture_path']]
        assert all(source.get(k) == e.get(k) for k in ['kind','mode','sha256','size','target'])
        assert e['action'] in ['directory-no-placeholder','copy-to-git','copy-to-annex','preserve-literal-link']
        dest = repo/e['path']; src = capture.parent/e['capture_path']
        assert not dest.exists() and not dest.is_symlink(), 'Publisher collision: '+e['path']
        assert stat.S_IMODE(src.lstat().st_mode) == e['mode']
        if e['kind'] == 'file':
            assert stat.S_ISREG(src.lstat().st_mode) and sha(src) == e['sha256'] and src.stat().st_size == e['size']
        elif e['kind'] == 'symlink': assert os.readlink(src) == e['target']
        else: assert e['kind'] == 'directory' and stat.S_ISDIR(src.lstat().st_mode)
    copied = []
    for e in plan['entries']:
        if e['action'] == 'directory-no-placeholder': continue
        dest = repo/e['path']; src = capture.parent/e['capture_path']; dest.parent.mkdir(parents=True, exist_ok=True)
        row = {'original_path':e['path'],'published_path':e['path'],'kind':e['kind'],'source_mode':e['mode']}
        if e['kind'] == 'symlink':
            os.symlink(e['target'], dest); row.update(storage='literal-link',target=e['target'])
        else:
            with src.open('rb') as source, dest.open('xb') as target: shutil.copyfileobj(source,target)
            os.chmod(dest,e['mode']); assert sha(dest) == sha(src) == e['sha256']
            row.update(bytes=e['size'],sha256=e['sha256'],storage='annex' if e['action']=='copy-to-annex' else 'git')
        copied.append(row)
    with (repo/'.gitattributes').open('a') as stream:
        stream.write('\n# Coordinator presentation copies; original scientific bytes unchanged.\n')
        for e in copied:
            stream.write(json.dumps('/'+e['published_path'])+' annex.largefiles='+('anything annex.backend=SHA256E' if e['storage']=='annex' else 'nothing')+'\n')
    annex = [e['published_path'] for e in copied if e['storage']=='annex']
    if annex: run(pixi+['git','annex','add','--force-large','--backend=SHA256E','--',*annex])
    for e in copied:
        if e['storage']=='annex': e['annex_key']=run(pixi+['git','annex','lookupkey',e['published_path']]).stdout.strip()
    evidence = repo/'coordinator/browsable-copy-01'; evidence.mkdir()
    shutil.copy2(plan_path,evidence/'plan.json'); shutil.copy2(inputs_path,evidence/'input-manifest.json')
    shutil.copy2(route_path,evidence/'shared-input-route-proof.json'); shutil.copy2(config_path,evidence/'config.json')
    shutil.copy2(Path(__file__),evidence/'prepare.py')
    manifest = {'schema':'coordinator-browsable-copy-v1','run_id':cfg['run_id'],'parent_commit':canonical['commit'],
      'source_worker_head':plan['original_worker_head'],'capture_sha256':sha(capture),'plan_sha256':sha(plan_path),
      'copied_files':copied,'authoritative_archive':'../delivery-01/delivery.tar.gz','authoritative_capture':'../original-manifest.json',
      'attribution':'Coordinator presentation copies of exact original stopped files; no worker credit or scientific execution.',
      'source_files_unchanged':True,'scientific_execution':False,'input_tree':inputs['input_tree'],
      'shared_input_route_proof_sha256':sha(route_path),'shared_input_manifest_sha256':sha(inputs_path),
      'shared_input_route_published_commit':cfg['input_route_published_proof_commit'],
      'input_verification_scope':'Exact Git input tree matches prior independently retrieved 58-payload input manifest; payloads not redundantly downloaded for this presentation.',
      'mode_scope':'Original full modes retained here and in authoritative archive; Git preserves executable bits and literal links, annex preserves payload bytes.'}
    save(evidence/'manifest.json',manifest)
    with (repo/'coordinator/README.md').open('a') as stream:
        stream.write('\n## Browsable original files\n\nOriginal scientific files are also available at their unchanged workspace paths. '
          'The [copy manifest](browsable-copy-01/manifest.json) records exact source hashes, original modes and storage choices. '
          'These are coordinator presentation copies; the complete archive remains authoritative. '
          'The input tree matches the [shared retrieval proof](browsable-copy-01/shared-input-route-proof.json); '
          'its 58 payloads were independently retrieved in the cited run 20 check. '
          'No scientific execution or worker credit is implied.\n')
    cmd=pixi+['pre-commit','run','--config',str(main/'.pre-commit-config.yaml'),'snapper','--files','coordinator/README.md']
    if run(cmd,allow=True).returncode: run(cmd)
    run(['git','add','--force','--','.gitattributes','coordinator/README.md','coordinator/browsable-copy-01',*[e['published_path'] for e in copied]])
    run(['git','diff','--cached','--check','--','.gitattributes','coordinator'])
    assert run(['git','diff','--cached','--name-only','--','input','coordinator/delivery-01','coordinator/original-manifest.json']).stdout == ''
    for e in copied:
        path=e['published_path']; mode=run(['git','ls-files','--stage','--',path]).stdout.split()[0]
        expected='120000' if e['storage'] in ['annex','literal-link'] else ('100755' if e['source_mode']&0o111 else '100644')
        assert mode == expected
        if e['kind']=='file': assert sha(repo/path) == e['sha256']
        else: assert os.readlink(repo/path) == e['target']
    assert sha(capture) == canonical['capture_sha256']
    assert run(['git','ls-tree','HEAD','coordinator/delivery-01/delivery.tar.gz']).stdout == archive_tree
    if not any(e['published_path']=='README.md' for e in copied):
        assert run(['git','ls-tree','HEAD','README.md']).stdout == original_readme
    diff=run(['git','diff','--cached','--stat']).stdout; (root/'prepared-diff-stat.txt').write_text(diff)
    (root/'prepared.patch').write_text(run(['git','diff','--cached','--binary']).stdout)
    save(root/'prepared.json',dict(manifest,publisher=str(repo),branch=cfg['branch'],annex_files=annex,
       package_index_sha256=canonical['package_index_sha256'],plan_path=str(plan_path),config_sha256=sha(config_path)))
    print(json.dumps({'prepared':True,'run_id':cfg['run_id'],'files':len(copied),'annex_files':len(annex),'committed':False}))
except BaseException:
    (root/'failure-prepare.txt').write_text(traceback.format_exc()); raise

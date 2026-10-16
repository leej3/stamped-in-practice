"""Retain successful publication proof, verify that commit, then fast-forward canonical."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,traceback
root=Path(sys.argv[1]).resolve();repo=root/'publisher';receiver=root/'fresh-check-01/recipient'
flow=Path(__file__).resolve().parent;cfg=json.loads((root/'config.json').read_text())
verified=json.loads((root/'fresh-check-01/result.json').read_text());published=json.loads((root/'publication.json').read_text())
assert verified['verified'] and verified['commit']==published['commit']
commands=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def run(argv,cwd=repo,_retry=False):
    p=subprocess.run(list(map(str,argv)),cwd=cwd,capture_output=True,text=True)
    commands.append({'argv':list(map(str,argv)),'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    save(root/'commands-finish.json',commands)
    if not _retry and p.returncode == 128 and 'ssh: connect to host github.com port 22: Operation timed out' in p.stderr and argv[:2] in [['git','fetch'],['git','ls-remote'],['git','push']]: return run(argv,cwd,True)
    p.check_returncode();return p.stdout.strip()
try:
    assert not (root/'final.json').exists()
    assert run(['git','rev-parse','HEAD'])==published['commit']
    assert run(['git','status','--porcelain'])==''
    target=repo/'coordinator/browsable-copy-01/evidence';target.mkdir()
    # Exact bounded receipts only; never recurse repositories or copy auth/profile state.
    paths=[p for p in root.iterdir() if p.is_file() and p.suffix in {'.json','.txt','.py'}]
    paths=[p for p in paths if p.name not in {'commands-finish.json','final.json'}]
    paths.extend([root/'fresh-check-01/commands.json',root/'fresh-check-01/result.json'])
    ledger=[]
    for source in sorted(paths):
        relative=source.relative_to(root);dest=target/relative;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,dest);assert sha(source)==sha(dest)
        ledger.append({'path':str(relative),'bytes':dest.stat().st_size,'sha256':sha(dest)})
    for name in ['commit.py','publish.py','verify-fresh.py','finish.py']:
        dest=target/'flow'/name;dest.parent.mkdir(exist_ok=True);shutil.copy2(flow/name,dest)
        ledger.append({'path':'flow/'+name,'bytes':dest.stat().st_size,'sha256':sha(dest)})
    save(target/'manifest.json',{'files':ledger,'verified_content_commit':published['commit'],
      'scope':'Coordinator preparation, publication and fresh payload retrieval proof. Original scientific bytes and archive remain unchanged.'})
    run(['git','add','--force','--','coordinator/browsable-copy-01/evidence'])
    assert all(p.startswith('coordinator/browsable-copy-01/evidence/') for p in run(['git','diff','--cached','--name-only']).splitlines())
    run(['git','diff','--cached','--check'])
    trailers=run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'])
    message=('docs(retention): retain browsable publication proof for '+cfg['run_id']+'\n\n'
      'Preserve coordinator source, commands, failures and independent payload\n'
      'retrieval receipts. Keep unchanged original scientific bytes and input\n'
      'tree distinct from this later coordinator evidence commit.\n\n'+trailers+'\n')
    (root/'proof-commit-message.txt').write_text(message);run(['git','commit','-F',root/'proof-commit-message.txt'])
    head=run(['git','rev-parse','HEAD'])
    assert run(['git','rev-parse','HEAD:input'])==cfg['canonical']['input_tree']
    run(['git','push','origin','HEAD:refs/heads/'+cfg['branch']])
    run(['git','fetch','--no-tags','origin',head],receiver)
    changed=run(['git','diff','--name-only',published['commit'],head],receiver).splitlines()
    assert all(p.startswith('coordinator/browsable-copy-01/evidence/') for p in changed)
    run(['git','checkout','--detach',head],receiver)
    assert sha(receiver/'coordinator/browsable-copy-01/evidence/manifest.json')==sha(target/'manifest.json')
    for item in ledger:assert sha(receiver/'coordinator/browsable-copy-01/evidence'/item['path'])==item['sha256']
    assert run(['git','status','--porcelain'],receiver)==''
    canonical_branch=cfg['canonical']['branch']
    remote_before=run(['git','ls-remote','origin','refs/heads/'+canonical_branch]).split()[0]
    assert remote_before==cfg['canonical']['commit'],'Unexpected canonical writer; stop without overwrite'
    run(['git','merge-base','--is-ancestor',remote_before,head])
    run(['git','push','origin','HEAD:refs/heads/'+canonical_branch])
    refs={x.split()[1]:x.split()[0] for x in run(['git','ls-remote','origin','refs/heads/'+canonical_branch,'refs/heads/'+cfg['branch']]).splitlines()}
    assert refs=={'refs/heads/'+canonical_branch:head,'refs/heads/'+cfg['branch']:head}
    assert sha(Path(cfg['plan_path']))==cfg['plan_sha256']
    capture=Path(json.loads(Path(cfg['plan_path']).read_text())['capture_manifest']['path'])
    assert sha(capture)==cfg['canonical']['capture_sha256']
    save(root/'final.json',{'run_id':cfg['run_id'],'commit':head,'content_commit':published['commit'],
      'canonical_parent':remote_before,'canonical_branch':canonical_branch,'browsable_branch':cfg['branch'],
      'dataset_id':cfg['canonical']['dataset_id'],'capture_sha256':cfg['canonical']['capture_sha256'],
      'input_tree':cfg['canonical']['input_tree'],'copied_files_verified':verified['copied_files_verified'],
      'fresh_proof_sha256':sha(root/'fresh-check-01/result.json'),'evidence_files_verified':len(ledger),
      'canonical_fast_forward_verified':True,'original_archive_unchanged':True,'scientific_execution':False,
      'command_log_sha256':sha(root/'commands-finish.json')})
    print(json.dumps(json.loads((root/'final.json').read_text())),flush=True)
except BaseException:
    (root/'failure-finish.txt').write_text(traceback.format_exc());raise

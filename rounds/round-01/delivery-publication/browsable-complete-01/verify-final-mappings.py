"""Read-only closure audit of the 23 explicitly assigned browsable datasets."""
from pathlib import Path
import collections,hashlib,json,os,stat,subprocess
root=Path(__file__).resolve().parent;base=root.parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def save(p,v):
    with p.open('x') as stream:stream.write(json.dumps(v,indent=2,sort_keys=True)+'\n')
names=['narps-neutral-r1-'+str(i).zfill(2) for i in range(1,25) if i!=20]
branches=['refs/heads/codex/'+name+suffix for name in names for suffix in ['-retained','-browsable']]
argv=['git','ls-remote','--refs','git@github.com:leej3/stamped-in-practice.git',*branches,'refs/heads/git-annex']
commands=[]
for attempt in range(2):
    p=subprocess.run(argv,capture_output=True,text=True)
    commands.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    if p.returncode==0:break
    if 'ssh: connect to host github.com port 22: Operation timed out' not in p.stderr:p.check_returncode()
save(root/'remote-check.json',{'commands':commands});p.check_returncode()
refs={line.split()[1]:line.split()[0] for line in p.stdout.splitlines()}
runs=[];counts=collections.Counter();retained_failures=[];command_failures=[]
for name in names:
    suffix=name.rsplit('-',1)[1];folder=base/('browsable-publication-r1-'+suffix+'-01')
    cfg=json.loads((folder/'config.json').read_text());final=json.loads((folder/'final.json').read_text())
    prepared=json.loads((folder/'prepared.json').read_text());plan=json.loads(Path(cfg['plan_path']).read_text())
    assert final['canonical_fast_forward_verified'] and final['original_archive_unchanged']
    assert refs['refs/heads/'+final['canonical_branch']]==refs['refs/heads/'+final['browsable_branch']]==final['commit']
    assert sha(folder/'fresh-check-01/result.json')==final['fresh_proof_sha256']
    capture=Path(plan['capture_manifest']['path']);assert sha(capture)==final['capture_sha256']
    native=base/'runs'/name/'attempt-01/native';stop=json.loads((native/'result.json').read_text())['worker_end_state']
    assert sha(native/'worker-end-state.json')==stop['sha256'] and stop['capture']['sha256']==final['capture_sha256']
    workspace=base/'workspaces'/name
    critical=['.git/HEAD','.git/config','.git/index']
    for relative in critical:assert (workspace/relative).read_bytes()==(capture.parent/'content/workspace'/relative).read_bytes()
    for entry in prepared['copied_files']:
        source=capture.parent/'content/workspace'/entry['original_path']
        assert stat.S_IMODE(source.lstat().st_mode)==entry['source_mode']
        if entry['kind']=='file':assert sha(source)==entry['sha256'] and source.stat().st_size==entry['bytes']
        else:assert os.readlink(source)==entry['target']
        counts[entry['storage']+'_files']+=1;counts[entry['storage']+'_bytes']+=entry.get('bytes',0)
    failures=[{'path':str(p),'sha256':sha(p)} for p in sorted(folder.glob('*failure*')) if p.is_file()]
    retained_failures.extend(failures)
    for log in sorted(folder.glob('commands-*.json')):
        for index, command in enumerate(json.loads(log.read_text())):
            if command.get('returncode',0):
                kind=('retained SSH timeout' if 'Operation timed out' in command.get('stderr','') else
                      'Snapper coordinator formatting pass' if 'snapper' in command.get('argv',[]) else
                      'retained command failure')
                command_failures.append({'run_id':name,'log':str(log),'log_sha256':sha(log),'entry_index':index,
                  'argv':command.get('argv'),'returncode':command['returncode'],'classification':kind})
    runs.append(dict(final,final_receipt=str(folder/'final.json'),final_receipt_sha256=sha(folder/'final.json'),
      original_stop_receipt_unchanged=True,original_critical_git_metadata_unchanged=True,
      copied_original_sources_revalidated=len(prepared['copied_files']),local_failures=failures))
assert len(runs)==23
save(root/'result.json',{'success':True,'runs':runs,'totals':dict(counts),'excluded_root_owned_run':'narps-neutral-r1-20',
 'shared_annex_commit':refs['refs/heads/git-annex'],'remote_check_sha256':sha(root/'remote-check.json'),
 'input_tree':runs[0]['input_tree'],'input_payload_route':'Prior root run20 independent 58-payload retrieval, with exact input-tree and manifest equality in every run.',
 'retained_local_failures':retained_failures,'nonzero_command_receipts':command_failures,
 'scope':'Coordinator presentation and preservation only; no scientific execution, original source changes, judging or study/main writes.'})
proofs=[]
for name in names:
    suffix=name.rsplit('-',1)[1];folder=base/('browsable-publication-r1-'+suffix+'-01')
    selected=[p for p in folder.iterdir() if p.is_file()]
    selected.extend(p for p in (folder/'fresh-check-01').iterdir() if p.is_file())
    proofs.extend(selected)
for folder in [base/'browsable-flow-01',base/'browsable-batch-01',base/'browsable-batch-02',base/'browsable-batch-03']:
    proofs.extend(p for p in folder.rglob('*') if p.is_file())
proofs.extend([root/'verify-final-mappings.py',root/'remote-check.json',root/'result.json'])
save(root/'proof-index.json',{'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(proofs))]})
for p in proofs+[root/'proof-index.json']:p.chmod(0o444)
print(json.dumps({'success':True,'runs':len(runs),'totals':dict(counts),'result_sha256':sha(root/'result.json'),'proof_index_sha256':sha(root/'proof-index.json')},indent=2))

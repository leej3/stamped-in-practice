"""Publish new-series native Git/Entire evidence with Hub transfers held."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,hashlib,json,os,shutil,subprocess,sys,traceback
R=Path(__file__).resolve().parent;B=R.parent;slot=sys.argv[1];runid=slot.rsplit('-j',1)[0]
C=json.loads((R/'coordinator-boundary.json').read_text());series=C['series_id'];seal=C['assessment_procedure_sha256']
out=R/'judgments'/slot;source=B/'assessment-series'/series/'judgments'/slot
assert (source/'completion.json').exists() and (source/'attempt-01/native/result.json').exists()
assert not (out/'completion-index.json').exists() and not (out/'git-completion-index.json').exists()
assert json.loads((out/'late-capture-01.integrity-audit.json').read_text())['verified']
locks=R/'locks';locks.mkdir(exist_ok=True);lock=(locks/(slot+'.lock')).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
pub=out/'native-publication-01';created=not pub.exists()
main=Path('/Users/johnlee/code/CON/stamped-in-practice');pixi=['pixi','run','--manifest-path',str(main/'pixi.toml'),'--locked']
resolver='/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def ref(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
if created:
 pub.mkdir();native=json.loads((source/'attempt-01/native/result.json').read_text());session,=native['native_session_ids']
 base=C['initial_bases'][runid];prior=[]
 for p in (R/'judgments').glob('*/*completion-index.json'):
  if p.parent.name==slot or p.parent.name.rsplit('-j',1)[0]!=runid:continue
  d=json.loads(p.read_text());prior.append((p,d.get('git_proof_commit',d.get('proof_commit'))))
 assert len(prior)<=1
 if prior:base=prior[0][1]
 config={'series_id':series,'assessment_procedure_sha256':seal,'slot':slot,'session_id':session,'judgment_root':str(source),'capture_root':str(out/'late-capture-01'),'base_commit':base,'initial_study_base':C['initial_bases'][runid],'prior_same_run_index':str(prior[0][0]) if prior else None,'branch':'codex/'+series+'-'+slot+'-native-publication','record_path':'coordinator/assessment-series/'+series+'/judgments/'+slot+'/native-publication-01'}
 for p in (R/'method-01').iterdir():
  if p.name not in ['preserve.py','audit-capture.py','frozen_delivery_snapshot.py']:shutil.copy2(p,pub/p.name)
 shutil.copy2(R/'hub-uuid-confirmation-01.json',pub/'hub-uuid-confirmation-01.json');save(pub/'publication-config.json',config)
phase=pub/'git-publication-01';phase.mkdir();shutil.copy2(Path(__file__),phase/'run-git-only-source.py')
repo=pub/'publisher';commands=[]
def run(label,argv,cwd=None,allow=False):
 argv=list(map(str,argv));cwd=cwd or repo
 # No Hub transfer/discovery commands are authorized in this stage.
 if 'annex' in argv:
  index=argv.index('annex');assert argv[index+1] in ['init','merge','add','lookupkey'],argv
 p=subprocess.run(argv,cwd=cwd,capture_output=True)
 (phase/(label+'.stdout')).write_bytes(p.stdout);(phase/(label+'.stderr')).write_bytes(p.stderr)
 commands.append({'label':label,'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':label+'.stdout','stderr':label+'.stderr'});save(phase/'commands.json',commands)
 if not allow:p.check_returncode()
 return p

def git(label,*args,cwd=None):return run(label,['git',*args],cwd).stdout.decode().strip()
def fresh_git(label,head,checkpoint=False):
 dest=pub/(label+'-fresh-check-01');dest.mkdir()
 git(label+'-init','init','--template=','--initial-branch','received',cwd=dest)
 git(label+'-remote','remote','add','origin','https://github.com/leej3/stamped-in-practice.git',cwd=dest)
 git(label+'-fetch','fetch','--no-tags','origin',head,cwd=dest)
 git(label+'-checkout','checkout','--detach','FETCH_HEAD',cwd=dest)
 assert not (dest/'.git/objects/info/alternates').exists()
 assert git(label+'-head','rev-parse','HEAD',cwd=dest)==head
 assert not git(label+'-originals','diff','--name-only',a['base_commit'],'HEAD','--','input','coordinator/delivery-01','coordinator/original-manifest.json',cwd=dest)
 if checkpoint:
  git(label+'-checkpoint-fetch','fetch','origin',a['checkpoint_ref']+':'+a['checkpoint_ref'],cwd=dest)
  assert git(label+'-checkpoint-oid','rev-parse',a['checkpoint_ref'],cwd=dest)==a['checkpoint_oid']
  meta=json.loads(git(label+'-checkpoint-metadata','show',a['checkpoint_ref']+':0/metadata.json',cwd=dest))
  assert meta['checkpoint_id']==a['checkpoint_id'] and meta['session_id']==a['session_id']
  raw=run(label+'-processed-transcript',['git','show',a['checkpoint_ref']+':0/full.jsonl'],dest).stdout
  assert hashlib.sha256(raw).hexdigest()==a['processed_sha256']
 return dest
try:
 if created:run('prepare-and-attach',[sys.executable,str(pub/'prepare-and-attach.py')],pub)
 a=json.loads((pub/'attachment.json').read_text());assert a['series_id']==series and a['assessment_procedure_sha256']==seal
 assert a['session_id'] not in {row['session_id'] for row in json.loads((B/'judge-native-publication-index-03/result.json').read_text())['records']}
 assert git('push-url','remote','get-url','--push','origin')=='git@github.com:leej3/stamped-in-practice.git'
 assert not git('initial-status','status','--porcelain')
 before_head=git('initial-head','rev-parse','HEAD');git('content-ancestor','merge-base','--is-ancestor',a['commit'],before_head)
 current=git('initial-remote','ls-remote','origin','refs/heads/'+a['branch'])
 if current:assert current.split()[0] in [a['commit'],before_head]
 git('push-code-checkpoint','push','origin','HEAD:refs/heads/'+a['branch'],a['checkpoint_ref']+':'+a['checkpoint_ref'])
 expected={'refs/heads/'+a['branch']:before_head,a['checkpoint_ref']:a['checkpoint_oid']}
 actual={line.split()[1]:line.split()[0] for line in git('content-refs','ls-remote','origin',*expected).splitlines()};assert actual==expected
 received=fresh_git('git-only',before_head,checkpoint=True)
 save(phase/'git-content-verification.json',{'verified':True,'checked_at':datetime.now(timezone.utc).isoformat(),'branch_head':before_head,'content_commit':a['commit'],'checkpoint_id':a['checkpoint_id'],'checkpoint_ref':a['checkpoint_ref'],'checkpoint_oid':a['checkpoint_oid'],'session_id':a['session_id'],'processed_transcript_sha256':a['processed_sha256'],'scope':'Independent empty Git store fetched exact GitHub code/checkpoint objects and processed checkpoint transcript. No Hub access or raw annex payload retrieval was attempted.'})
 n=1
 while (pub/('hosted-check-'+str(n).zfill(2))).exists():n+=1
 hosted=pub/('hosted-check-'+str(n).zfill(2));run('hosted-verification',[sys.executable,str(pub/'verify-hosted.py'),str(n).zfill(2)],pub)
 assert json.loads((hosted/'result.json').read_text())['hosted_verified']
 rel=Path(a['coordinator_record_path'])/'git-stage-01';dest=repo/rel;dest.mkdir();files={}
 sources=[p for p in pub.iterdir() if p.is_file()]
 for p in pub.iterdir():
  if p.is_dir() and (p.name.startswith('hosted-check-') or p.name.startswith('proof-publication-') or p.name=='git-publication-01'):
   sources.extend(q for q in p.rglob('*') if q.is_file() and not q.is_symlink())
 # Keep all exact earlier failure evidence, including wrapper stdout/stderr.
 sources.extend(p for p in out.iterdir() if p.is_file() and p.name not in ['result.json','git-completion-index.json'])
 for p in sorted(set(sources)):
  name=Path('publication')/p.relative_to(pub) if p.is_relative_to(pub) else Path('pipeline')/p.name
  q=dest/'evidence'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
  files[str(q.relative_to(repo))]={'source':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
 capture=out/'late-capture-01'
 save(dest/'capture-links.json',{'full_local_capture_manifest':ref(capture/'manifest.json'),'local_integrity_audit':ref(out/'late-capture-01.integrity-audit.json'),'source_to_captured_mapping':ref(capture/'source-captures.json'),'full_capture_publication_owner':'formal_coordinator','scope':'Complete raw attempt/guidance/canonical/operational/delta/replay bytes are retained in the local capture; this native branch publishes selected native evidence and truthful transport status.'})
 bulk=[p for p,v in files.items() if v['bytes']>=1024*1024 or p.endswith('processed-transcript.stdout')]
 if bulk:
  with (repo/'.gitattributes').open('a') as f:
   f.write('\n# Git-only native proof payloads; Hub verification remains pending.\n')
   for p in bulk:f.write(json.dumps('/'+p)+' annex.largefiles=anything annex.backend=SHA256E\n')
  run('annex-local-evidence',pixi+['git','annex','add','--force-large','--backend=SHA256E','--',*bulk])
 existing=list(a['annex_paths'])
 prior_manifest=repo/a['coordinator_record_path']/'evidence/manifest.json'
 if prior_manifest.exists():
  previous=json.loads(prior_manifest.read_text())['files'];existing.extend(p for p,v in previous.items() if v['bytes']>=1024*1024 or p.endswith('processed-transcript.stdout'))
 payloads=[]
 for i,p in enumerate(sorted(set(existing+bulk))):
  q=repo/p;key=run('payload-key-'+str(i),pixi+['git','annex','lookupkey',p]).stdout.decode().strip()
  uploaded=(pub/'publication.json').exists() and p in a['annex_paths']
  prior_proof_uploaded=(pub/'proof-publication-01/upload-evidence.stdout').exists() and p in existing and p not in a['annex_paths']
  payloads.append({'path':p,'annex_key':key,'sha256':sha(q),'bytes':q.stat().st_size,'hub_upload_status':'previously_succeeded' if uploaded or prior_proof_uploaded else 'not_attempted_held','fresh_hub_retrieval_status':'previously_verified' if uploaded and (pub/'fresh-verification.json').exists() else ('failed_proxy_error_in_initial_recipient' if prior_proof_uploaded else 'not_attempted_held')})
 save(dest/'pending-payloads.json',{'series_id':series,'slot':slot,'hub_transfers_held':True,'payloads':payloads,'scope':'Exact bytes/keys and stage-specific receipt status. Not-attempted does not assert remote absence. The source data are locally preserved; hosted identity and Git checkpoint bytes are independently verified.'})
 save(dest/'status.json',{'series_id':series,'assessment_procedure_sha256':seal,'slot':slot,'session_id':a['session_id'],'checkpoint_id':a['checkpoint_id'],'content_commit':a['commit'],'branch_head_before_proof':before_head,'git_content_and_checkpoint_verified':True,'hosted_checkpoint_verified':True,'fully_verified_hub_publication':False,'hub_transfers_held':True,'historical_attachment_after_session_end':True,'raw_sha256':a['raw_sha256'],'attached_processed_sha256':a['processed_sha256'],'hosted_verification':ref(hosted/'result.json'),'failed_attempts_retained':[str(p.relative_to(pub)) for p in pub.glob('**/failure.txt') if not any('fresh-check' in part or part=='publisher' for part in p.relative_to(pub).parts)],'scientific_validity_assessed':False})
 save(dest/'manifest.json',{'evidence_files':files,'scope':'Evidence source snapshot before this Git proof commit. Commit and final fresh-Git verification logs are retained separately; Hub payload verification remains pending.'})
 git('stage','add','--force','--','.gitattributes',a['coordinator_record_path'])
 names=git('staged-scope','diff','--cached','--name-only').splitlines();assert all(p=='.gitattributes' or p.startswith(str(rel)+'/') for p in names)
 git('diff-check','diff','--cached','--check')
 trailers=run('provenance',[resolver]).stdout.decode().strip();assert 'Co-Authored-By:' in trailers and 'Codex-Reasoning-Effort:' in trailers
 message=phase/'message.txt';message.write_text('chore(narps): publish native Git proof with Hub retrieval pending\n\nRetain verified Git checkpoint and hosted-session evidence separately from\nHub payload upload and retrieval. Preserve exact pending keys and failures.\nThis coordinator publication follows the original judge session stop.\n\n'+trailers+'\n')
 git('commit','-c','core.hooksPath=/dev/null','commit','-F',str(message));head=git('proof-head','rev-parse','HEAD')
 git('push-git-proof','push','origin','HEAD:refs/heads/'+a['branch'])
 for n in range(4):
  git('annex-fetch-'+str(n),'fetch','origin','+git-annex:refs/remotes/origin/git-annex')
  shared=git('annex-shared-'+str(n),'rev-parse','refs/remotes/origin/git-annex');run('annex-merge-'+str(n),pixi+['git','annex','merge'])
  git('annex-ancestor-'+str(n),'merge-base','--is-ancestor',shared,'git-annex')
  p=run('annex-push-'+str(n),['git','push','origin','git-annex:git-annex'],allow=True)
  if p.returncode==0:break
  assert any(x in p.stderr for x in [b'non-fast-forward',b'fetch first',b"cannot lock ref 'refs/heads/git-annex': is at"])
 else:raise RuntimeError('GitHub annex metadata publication did not converge')
 fresh=fresh_git('git-proof',head,checkpoint=True)
 for p,row in files.items():
  if p in bulk:
   assert (fresh/p).is_symlink() and not (fresh/p).exists()
   assert os.readlink(fresh/p)==os.readlink(repo/p)
  else:assert sha(fresh/p)==row['sha256'] and (fresh/p).stat().st_size==row['bytes']
 for name in ['capture-links.json','pending-payloads.json','status.json','manifest.json']:assert sha(fresh/rel/name)==sha(repo/rel/name)
 assert {p:sha(Path(p)) for p in a['original_sources_unchanged']}==a['original_sources_unchanged']
 assert not git('publisher-final-status','status','--porcelain')
 expected={'refs/heads/'+a['branch']:head,a['checkpoint_ref']:a['checkpoint_oid']};actual={line.split()[1]:line.split()[0] for line in git('final-refs','ls-remote','origin',*expected).splitlines()};assert actual==expected
 result={'schema':'operational-native-git-stage-v1','finished_at':datetime.now(timezone.utc).isoformat(),'series_id':series,'assessment_procedure_sha256':seal,'slot':slot,'session_id':a['session_id'],'branch':a['branch'],'content_commit':a['commit'],'git_proof_commit':head,'checkpoint_id':a['checkpoint_id'],'checkpoint_ref':a['checkpoint_ref'],'checkpoint_oid':a['checkpoint_oid'],'git_code_checkpoint_and_proof_verified':True,'hosted_checkpoint_verified':True,'fully_verified_hub_publication':False,'hub_transfers_held':True,'annex_payloads':payloads,'raw_transcript_sha256':a['raw_sha256'],'processed_transcript_sha256':a['processed_sha256'],'historical_attachment_after_session_end':True,'capture_manifest':ref(capture/'manifest.json'),'capture_integrity_audit':ref(out/'late-capture-01.integrity-audit.json'),'hosted_verification':ref(hosted/'result.json'),'git_content_verification':ref(phase/'git-content-verification.json'),'git_proof_manifest_sha256':sha(repo/rel/'manifest.json'),'scope':'Independent GitHub code/checkpoint/proof retrieval and authenticated hosted identity only. Raw native annex payloads and full proof payloads retain their individual pending Hub statuses. No complete-publication claim.'}
 save(phase/'result.json',result);save(out/'git-completion-index.json',dict(result,git_stage_result=ref(phase/'result.json')))
 print(json.dumps({'slot':slot,'git_proof_commit':head,'checkpoint_id':a['checkpoint_id'],'git_completion_index':ref(out/'git-completion-index.json'),'fully_verified_hub_publication':False}),flush=True)
except Exception:
 (phase/'failure.txt').write_text(traceback.format_exc());raise

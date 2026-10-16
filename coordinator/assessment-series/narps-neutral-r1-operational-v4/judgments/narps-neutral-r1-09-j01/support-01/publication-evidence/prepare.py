"""Publish exact closed support; only coordinator-attributed new paths."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parent;cfg=json.loads((R/'config.json').read_text());B=R.parent;M=Path('/Users/johnlee/code/CON/stamped-in-practice');P=Path(cfg['package']);E=Path(cfg['extraction']);slot=cfg['slot'];series='narps-neutral-r1-operational-v4';repo=R/'publisher';root=Path('coordinator/assessment-series')/series/'judgments'/slot;dest=root/'support-01';commands=[];PX=['pixi','run','--manifest-path',str(M/'pixi.toml'),'--locked']
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def run(args,cwd=R,allow=False):
 args=list(map(str,args));p=subprocess.run(args,cwd=cwd,capture_output=True,text=True);commands.append({'argv':args,'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});save(R/'prepare-commands.json',commands)
 if not allow:p.check_returncode()
 return p.stdout.strip() if not allow else p

def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def copy(s,d):
 assert s.is_file() and not s.is_symlink(),s
 before=sha(s);d.parent.mkdir(parents=True,exist_ok=True);assert not d.exists();shutil.copy2(s,d);assert before==sha(s)==sha(d)

v=json.loads((P/'package-verification.json').read_text());i=json.loads((P/'completion-index.json').read_text());assert v['verified'] and v['source_before_after_equal'] and v['slot']==slot and v['closed_index_sha256']==sha(P/'completion-index.json');assert sha(P/'support.tar.gz')==v['archive_sha256'];base=i['proof_commit'];assert base==v['native_publication_base'];branch='codex/'+slot+'-operational-v4-support-01'
run(['git','init','--initial-branch',branch,repo]);run(['git','remote','add','origin','https://github.com/leej3/stamped-in-practice.git'],repo);run(['git','remote','set-url','--push','origin','git@github.com:leej3/stamped-in-practice.git'],repo);run(['git','fetch','--no-tags','origin',base],repo);run(['git','reset','--hard','FETCH_HEAD'],repo);assert not(repo/'.git/objects/info/alternates').exists();run(['git','config','remote.origin.annex-ignore','true'],repo)
host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_text());run(PX+['git','annex','init',slot+' separate assessment support'],repo);run(['git','remote','add',host['annex_remote'],host['annex_git_url']],repo);run(['git','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url']],repo)
for s in sorted(P.iterdir()):
 if s.is_file():copy(s,repo/dest/s.name)
idx=json.loads((E/'index.json').read_text());entries=[j for r in idx['runs'] for j in r.get('judgments',{}).values() if j.get('judgment_id')==slot];assert len(entries)==1
refs=[]
def collect(obj):
 if isinstance(obj,dict):
  if set(obj)=={'path','sha256'}:refs.append(obj)
  else:
   for value in obj.values():collect(value)
 elif isinstance(obj,list):
  for value in obj:collect(value)
collect(entries[0]);bindings=[]
for ref in refs:
 s=E/ref['path'];assert sha(s)==ref['sha256'];d=root/'assessment'/Path(ref['path']).name
 if not (repo/d).exists():copy(s,repo/d)
 else:assert sha(repo/d)==ref['sha256']
 bindings.append({'source':str(s),'destination':str(d),'sha256':ref['sha256']})
save(repo/dest/'readable-copy-map.json',{'extraction_index_sha256':sha(E/'index.json'),'judgment':entries[0],'copies':bindings,'scope':'Exact coordinator presentation copies; source report wording and raw grades unchanged.'})
(repo/dest/'README.md').write_text(f'''# Separate assessment support: {slot}

This is a new measurement of the original research delivery under the separately registered operational-copy procedure. The original assessment remains in its earlier coordinator paths.

Read the exact [judge report](../assessment/report.md), [checklist response](../assessment/response.json) and [structured scientific record](../assessment/scientific-judgment.json). The [copy map](readable-copy-map.json) binds their source bytes; report-local probe and replay paths resolve inside the complete archived judgment workspace.

The [support archive](support.tar.gz) preserves the complete stopped attempt, raw native transcript, original live Entire shadow, later hosted attachment representation, canonical and operational copies, final operational delta, replay artifacts, supplied guidance, and every retained failure. The [member manifest](member-manifest.json), [source closure](completion-index.json) and [verification](package-verification.json) bind all bytes, modes and literal links. Only three independently verified publisher/recipient caches are excluded, as listed in the closure.

Archive members use `evidence/` followed by the source closure's relative path. This is coordinator preservation and publication; it earns no worker-practice credit and changes no scientific file or judgment. Raw and processed native representations remain distinct.

Retrieve large payloads using the [shared guide](https://github.com/leej3/stamped-in-practice/blob/main/RETRIEVAL.md).
''')
nav=repo/'coordinator/README.md';assert nav.is_file();oldnav=nav.read_text();nav.write_text(oldnav+f'\n## Separate operational assessment\n\n[{slot} report and complete evidence](assessment-series/{series}/judgments/{slot}/support-01/README.md) belong to the separately registered measurement series; the original assessment remains unchanged.\n')
attrs=repo/'.gitattributes';attrs.write_text(attrs.read_text()+f'\n# Exact separate-series support; authored navigation and readable copies in Git.\n{root}/support-01/** annex.largefiles=nothing\n{root}/assessment/** annex.largefiles=nothing\n{dest}/support.tar.gz annex.largefiles=anything annex.backend=SHA256E\n')
run(['snapper','--in-place','coordinator/README.md',dest/'README.md'],repo)
files=[]
for top in [repo/dest,repo/root/'assessment']:
 for p in sorted(top.rglob('*')):
  if p.is_file():files.append({'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)})
save(repo/dest/'publication-files.json',files)
run(PX+['git','annex','add','--force-large','--backend=SHA256E','--',dest/'support.tar.gz'],repo);key=f"SHA256E-s{v['archive_bytes']}--{v['archive_sha256']}.tar.gz";assert run(PX+['git','annex','lookupkey',dest/'support.tar.gz'],repo)==key
run(['git','add','.gitattributes','coordinator'],repo);paths=run(['git','diff','--cached','--name-only'],repo).splitlines();assert paths and all(p=='.gitattributes' or p=='coordinator/README.md' or p.startswith(str(root)+'/') for p in paths)
run(['git','diff','--cached','--check','--','.gitattributes','coordinator/README.md',dest/'README.md'],repo)
trailers=run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'],repo);msg=R/'commit-message.txt';msg.write_text('data(assessment): preserve separate-series complete support\n\nRetain the exact closed delivery, full native evidence and operational\ncopy changes. Add readable judgment copies without altering the original\nseries, scientific files or worker-practice attribution.\n\n'+trailers+'\n');run(['git','commit','-F',msg],repo);head=run(['git','rev-parse','HEAD'],repo);assert run(['git','rev-parse','HEAD^'],repo)==base;assert run(['git','rev-parse','HEAD:input'],repo)==run(['git','rev-parse',base+':input'],repo);assert not run(['git','status','--porcelain'],repo)
save(R/'prepared.json',{'run_id':slot.rsplit('-j',1)[0],'slot':slot,'series_id':series,'base':base,'commit':head,'branch':branch,'publisher':str(repo),'support_path':str(dest),'archive_path':str(dest/'support.tar.gz'),'archive_key':key,'archive_sha256':v['archive_sha256'],'archive_bytes':v['archive_bytes'],'publication_manifest_sha256':sha(repo/dest/'publication-files.json'),'scope':'Coordinator support only; original delivery and both assessment series unchanged.'});print(head)

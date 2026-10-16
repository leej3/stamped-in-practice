from pathlib import Path
import subprocess,json,hashlib,shutil
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');D=B/'dataset';R=Path(__file__).resolve().parent;M=Path('/Users/johnlee/code/CON/stamped-in-practice');P=['pixi','run','--manifest-path',str(M/'pixi.toml'),'--locked'];C=D/'rounds/round-01/synthesis/publication-evidence';C.mkdir();cmds=[]
def run(argv,cwd=D):
 argv=list(map(str,argv));p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True);cmds.append({'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});(R/'finalize-commands.json').write_text(json.dumps(cmds,indent=2)+'\n');p.check_returncode();return p.stdout.strip()
files=[]
for f in sorted(R.iterdir()):
 if f.is_file() and not f.name.startswith('finalize-') and f.name not in ['finalize.stdout','finalize.stderr']:
  dest=C/f.name;shutil.copy2(f,dest);files.append({'path':str(dest.relative_to(D)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(C/'.gitattributes').write_text('* annex.largefiles=nothing\n');(C/'manifest.json').write_text(json.dumps({'scope':'Complete synthesis preparation, source/table reproduction, publication and cold retrieval receipts; initial unlocked-pointer check failure retained. This proof commit is verified separately.','files':files},indent=2)+'\n')
old=run(['git','rev-parse','HEAD']);assert old=='9ff24fcfaeaeb1d96ba52bf676c11393463ade43';run(P+['git','add','--',C]);tr=run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh']);msg=R/'finalize-message.txt';msg.write_text('chore(evidence): retain round synthesis publication proof\n\nPreserve source-table reproduction and independent cold retrieval of\nall changed files, including regular annex pointers and their payloads.\n\n'+tr+'\n');run(['git','commit','-F',msg]);head=run(['git','rev-parse','HEAD']);run(['git','push','origin','HEAD:refs/heads/codex/iteration-narps-neutral-v1'])
rec=R/'fresh-recipient';run(['git','fetch','--no-tags','origin',head],rec);changed=run(['git','diff','--name-only',old,head],rec).splitlines();assert all(p.startswith('rounds/round-01/synthesis/publication-evidence/') for p in changed);run(['git','checkout','--detach',head],rec)
for f in files:assert hashlib.sha256((rec/f['path']).read_bytes()).hexdigest()==f['sha256']
assert (rec/C.relative_to(D)/'manifest.json').read_bytes()==(C/'manifest.json').read_bytes();assert run(['git','status','--porcelain'],rec)==''
(R/'finalize-result.json').write_text(json.dumps({'verified':True,'commit':head,'content_commit':old,'new_proof_files':len(changed),'original_tables_figures_unchanged':True,'recipient':str(rec)},indent=2)+'\n');print(head)

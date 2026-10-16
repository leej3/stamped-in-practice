from pathlib import Path
import json,subprocess,hashlib
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');R=Path(__file__).resolve().parent;D=B/'dataset';rec=R/'fresh-recipient';M=Path('/Users/johnlee/code/CON/stamped-in-practice');P=['pixi','run','--manifest-path',str(M/'pixi.toml'),'--locked'];host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_bytes());cmds=[]
def run(argv,cwd=rec):
 argv=list(map(str,argv));p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True);cmds.append({'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});(R/'retrieval-02-commands.json').write_text(json.dumps(cmds,indent=2)+'\n');p.check_returncode();return p.stdout.strip()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
annex=json.loads((R/'annex-files.json').read_bytes());files=json.loads((R/'publication-files.json').read_bytes());absence=[]
for r in annex:
 p=rec/r['file']
 if p.is_symlink():assert not p.exists();absence.append({'path':r['file'],'representation':'unmaterialized symlink','link':str(p.readlink())})
 else:
  data=p.read_bytes();assert data==('/annex/objects/'+r['key']+'\n').encode(),r['file'];absence.append({'path':r['file'],'representation':'regular unlocked annex pointer','pointer_sha256':hashlib.sha256(data).hexdigest()})
(R/'initial-annex-representation-02.json').write_text(json.dumps({'payloads_absent':True,'paths':absence,'original_failed_check':'publish.stderr','limitation':'exists() alone is not annex materialization proof; original check failure remains retained.'},indent=2)+'\n')
assert not(rec/'.git/objects/info/alternates').exists()
run(P+['git','annex','init','independent round-one synthesis recipient']);run(['git','remote','add',host['annex_remote'],host['annex_git_url']]);run(['git','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url']]);run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex']);run(P+['git','annex','merge']);run(P+['git','annex','get','--from',host['annex_remote'],'--',*[r['file'] for r in annex]])
for r in files:assert sha(rec/r['path'])==r['sha256'] and (rec/r['path']).stat().st_size==r['bytes'],r['path']
assert run(['git','status','--porcelain'])=='';head=run(['git','rev-parse','HEAD']);assert head=='9ff24fcfaeaeb1d96ba52bf676c11393463ade43'
for p in ['rounds/round-01/synthesis/attrition/assessment-attrition.png','rounds/round-01/synthesis/figures/scientific-adequacy.png']:assert run(['git','ls-tree','HEAD',p]).startswith('100644 ')
result={'verified':True,'commit':head,'files_verified':len(files),'annex_payload_paths_freshly_retrieved':len(annex),'all_changed_payload_bytes_verified':True,'no_git_alternates':True,'frozen_records_unchanged':True,'figures_git_browsable':True,'recipient':str(rec),'initial_pointer_detection_failure_preserved':True};(R/'publication-result-complete.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

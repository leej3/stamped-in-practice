"""Publish one already-verified coordinator bundle above an immutable result."""
from pathlib import Path
import argparse,datetime,json,subprocess,shutil,hashlib
p=argparse.ArgumentParser();p.add_argument('run');a=p.parse_args();repo=Path('/Users/johnlee/code/CON/stamped-in-practice');base=Path.home()/'.local/state/stamped-in-practice/narps-v1';stage=base/'staged-retention'/a.run;bundle=stage/'publishable-bundle-01';proof=json.loads((bundle/'bundle-receipt.json').read_text());assert proof['status']=='verified';result=proof['scientific_result'];w=stage/'retention-checkout';assert not w.exists();out=stage/'publication-01';out.mkdir();rec={'run':a.run,'scientific_result':result,'bundle_receipt_sha256':hashlib.sha256((bundle/'bundle-receipt.json').read_bytes()).hexdigest(),'actor':'coordinator','commands':[]}
def save(): (out/'commands.json').write_text(json.dumps(rec,indent=2)+'\n')
def run(argv,cwd=repo):
 started=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(argv,cwd=cwd,capture_output=True,text=True);rec['commands'].append({'argv':argv,'cwd':str(cwd),'started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});save();assert r.returncode==0,(argv,r.stderr);return r.stdout
run(['git','clone','--single-branch','--branch','codex/'+a.run,'git@github.com:leej3/stamped-in-practice.git',str(w)]);assert run(['git','-C',str(w),'rev-parse','HEAD']).strip()==result;branch='codex/'+a.run+'-retained';run(['git','-C',str(w),'switch','-c',branch]);host=json.loads((Path.home()/'.config/stamped-in-practice/launch.json').read_text());run(['git','-C',str(w),'remote','add',host['annex_remote'],host['annex_git_url']]);run(['git','-C',str(w),'config','remote.'+host['annex_remote']+'.annexurl',host['annex_url']]);run(['git','-C',str(w),'config','remote.origin.annex-ignore','true']);run(['git','-C',str(w),'fetch','origin','git-annex:refs/remotes/origin/git-annex']);run(['pixi','run','--locked','git','-C',str(w),'annex','init','coordinator retention '+a.run]);run(['pixi','run','--locked','git','-C',str(w),'annex','merge']);dest=w/'coordinator/retention-01';shutil.copytree(bundle,dest)
readme=f'''# Coordinator retention after the scientific result

The judged scientific result is `{result}`.
This directory was added afterward by the coordinator and earns no worker credit.
It retains the original worker stop, execution evidence, assigned assessments, native capture, failed attempts, environment snapshots and observed skills.

`package.tar.gz` contains the complete staged evidence package, including embedded Git stores and exact symlink text.
`package-manifest.json` inventories retained source paths and byte hashes; its plan identifies any reconstructable cache exclusions and their included proofs.
`bundle-receipt.json` records archive verification and exact directly readable copies under `indexable/`.
Canonical reports and response JSON remain unchanged; assignments and external measure-validity overlays belong to the iteration records.
Historical absolute paths and dangling annex links describe captured state, not current access.

Retrieve annex content through an authorized remote and inspect the archive with standard tar tools.
Retained retrieval receipts identify the tested routes and their same-host scope.
This is coordinator preservation, not an additional scientific run or a successful-replay claim.
''';(dest/'README.md').write_text(readme);shutil.copyfile(__file__,dest/'publish_bundle.py');run(['snapper','--in-place',str(dest/'README.md')]);run(['pixi','run','--locked','git','-C',str(w),'annex','add','coordinator/retention-01']);paths=run(['git','-C',str(w),'diff','--cached','--name-only']).splitlines();assert paths and all(x.startswith('coordinator/retention-01/') for x in paths)
# Resolve attribution immediately before this authored retention commit.
trailers=run([str(Path.home()/'.agents/skills/commit-provenance/scripts/resolve.sh')]).strip();assert 'Co-Authored-By:' in trailers and 'Codex-Reasoning-Effort:' in trailers
message=f'chore(retention): preserve {a.run} coordinator evidence\n\nAdd complete verified evidence above the unchanged scientific result.\nKeep raw judgments, failed attempts and separate coordinator attribution.\n\n{trailers}\n';msg=out/'commit-message.txt';msg.write_text(message);run(['git','-C',str(w),'commit','-F',str(msg)]);commit=run(['git','-C',str(w),'rev-parse','HEAD']).strip();assert run(['git','-C',str(w),'rev-parse','HEAD^']).strip()==result;rec['retention_commit']=commit;rec['branch']=branch;save();run(['git','-C',str(w),'push','origin',branch]);run(['pixi','run','--locked','git','-C',str(w),'annex','copy','--to',host['annex_remote'],'--json','--','coordinator/retention-01']);run(['git','-C',str(w),'fetch','origin','git-annex:refs/remotes/origin/git-annex']);run(['pixi','run','--locked','git','-C',str(w),'annex','merge']);run(['git','-C',str(w),'push','origin','git-annex']);rec['published_annex_metadata']=run(['git','-C',str(w),'rev-parse','git-annex']).strip();rec['publication_complete']=True;save();print(json.dumps({k:v for k,v in rec.items() if k!='commands'}))

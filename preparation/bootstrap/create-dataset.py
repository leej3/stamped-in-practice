from pathlib import Path
import json,subprocess
root=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
dataset=root/'dataset'
coordinator=Path('/Users/johnlee/code/CON/stamped-in-practice')
records=[]
def run(argv,cwd):
 r=subprocess.run(list(map(str,argv)),cwd=cwd,capture_output=True,text=True)
 records.append({'argv':list(map(str,argv)),'cwd':str(cwd),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 (root/'create-dataset-commands.json').write_text(json.dumps(records,indent=2)+'\n')
 r.check_returncode();return r.stdout.strip()
run(['git','init','-b','codex/iteration-narps-neutral-v1',dataset],coordinator)
trailers=run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'],coordinator)
message='chore(dataset): initialize prospective neutral comparison\n\nCreate a separate DataLad dataset for the new fixed comparison.\nNative operation: DataLad create --force.\n\n'+trailers
run(['pixi','run','--locked','datalad','create','--force','--description','Prospective tool-neutral NARPS comparison','--message',message,dataset],coordinator)
run(['git','remote','add','origin','git@github.com:leej3/stamped-in-practice.git'],dataset)
run(['git','remote','add','con-hub','https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git'],dataset)
run(['git','config','remote.con-hub.annexurl','annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp'],dataset)
run(['git','config','remote.origin.annex-ignore','true'],dataset)
print(json.dumps({'dataset':str(dataset),'commit':run(['git','rev-parse','HEAD'],dataset),'dataset_id':run(['git','config','--file','.datalad/config','--get','datalad.dataset.id'],dataset)}))

from pathlib import Path
import json,hashlib,sys,argparse,subprocess,collections
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');M=Path('/Users/johnlee/code/CON/stamped-in-practice');C=Path('/Users/johnlee/.local/share/wt-utils/worktrees/4af0/stamped-in-practice');OLD=Path('/Users/johnlee/.local/share/wt-utils/worktrees/6973/stamped-in-practice');R=B/'round-02-contract-review-01'
sys.path.insert(0,str(OLD/'scripts'))
import assessment_procedure as procedure
from study_seed import snapshot_research_skills
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=B/'dataset/procedure.json';digest='b011f6e68dc6838e736f1ae2ad70d52896dab9b848d6f33950b4d35dd86b1521';manifest=procedure.load_procedure(seal,digest)
base='9068886f91615b2c69578bdaa6042a858f4d9011';skills='d83d7d66a9060be6afae57336124afdcfc1743e9'
# Use the exact original verifier against committed objects in the main Git
# store. Main's evolving working files are intentionally not the launch source.
procedure.check_sources(manifest,M,M/'studies/narps',base,validate_working=False)
for name,dig in manifest['fixed_files'].items():
 assert sha(C/name)==dig and sha(OLD/name)==dig,name
assert procedure.gitmodules_digest((C/'.gitmodules').read_bytes())==manifest['gitmodules_sha256']
host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_bytes());host.update(role='research',capture_execution=True,common_resources=B/'dataset/resources/common-resources.md')
args=argparse.Namespace(**host)
procedure.check_settings(manifest,args);procedure.check_host(manifest,args);procedure.check_readiness(manifest,B/'readiness-01/result.json');procedure.check_native(manifest,Path(host['cli']),Path(host['codex_home']),'research')
assert subprocess.check_output(['git','rev-parse',base+':skills'],cwd=M,text=True).strip()==skills
files=snapshot_research_skills(M/'skills',skills,R/'skill-snapshot');assert files
(R/'skill-files.json').write_text(json.dumps(files,indent=2)+'\n')
allocation=B/'dataset/allocation.json';a=json.loads(allocation.read_bytes());r=a['rounds'][1];assert r['round']==2 and r['research_guidance_pin'] is None
assert len(r['launch_order'])==24 and len(r['judgment_dispatch_order'])==32 and len(r['duplicate_judgments'])==8
assert set(collections.Counter(x['condition'] for x in r['launch_order']).values())=={6}
result={'verified':True,'scope':'Unlaunched contract review; no seed commit, native session, research result or new seal created.','research_procedure_sha256':digest,'original_verifier_source':str(OLD),'prospective_source':base,'prospective_skill_pin':skills,'fixed_files_verified':len(manifest['fixed_files']),'committed_source_guard_passed':True,'candidate_and_original_working_files_match':True,'host_settings_native_readiness_checks_passed':True,'supplied_skill_snapshot_files':len(files),'allocation_sha256':sha(allocation),'round2_workers':24,'round2_assigned_judgments':32,'new_research_seal_required':False,'prelaunch_record_required':'Additive round-two skill/source binding and dispatch record; preserve original allocation/seal bytes.','launch_preparation_remaining':'Install only selected study input in candidate checkout (or use original driver checkout with its own selected study installed), verify materialized original input bytes, and run normal preflight at dispatch.','assessment_followup':'After original deliveries close, bind round2 exact seed/HEAD/stop/capture identities in a new v4 assessment seal using unchanged4f72 mechanism/settings/source and original research seal; same32 allocated slots. New object-binding digest is not a new measurement mechanism.'}
(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

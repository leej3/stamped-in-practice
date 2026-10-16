"""Additive late preservation of one naturally completed judge. No science runs.
Reuses frozen delivery_snapshot read primitives, not its research stop writer.
Copies all attempt/output bytes, including ignored/failed/replay material; never
follows arbitrary links. All original Git reads are avoided except fixed assessor
pin reads; judge Git reads use the new copy with optional locks disabled.
"""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,stat,subprocess,sys,traceback
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
spec=importlib.util.spec_from_file_location('frozen_capture',HERE/'frozen_delivery_snapshot.py');F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
sha=lambda data:hashlib.sha256(data).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
parser=argparse.ArgumentParser();parser.add_argument('judgment');args=parser.parse_args()
assert re.fullmatch(r'narps-neutral-r1-\d{2}-j\d{2}',args.judgment)
identifier=args.judgment;run=identifier.rsplit('-j',1)[0]
judgment=BASE/'runs'/run/'judgments'/identifier;attempt=judgment/'attempt-01'
dispatch_bytes=(judgment/'dispatch.json').read_bytes();dispatch=json.loads(dispatch_bytes)
assert dispatch['status']=='launcher-finished' and isinstance(dispatch['returncode'],int) and dispatch['finished_utc']
result_bytes=(attempt/'native/result.json').read_bytes();result=json.loads(result_bytes)
assert result['role']=='judge' and result['finished_at'] and isinstance(result['returncode'],int) and result['timed_out'] is False
workspace=Path(result['judge_workspace']);profile=Path(result['codex_home']);sessions=result['native_session_ids']
assert workspace==attempt/'judgment' and result['cwd']==str(workspace) and len(sessions)==1
assert not workspace.is_symlink() and not attempt.is_symlink() and not profile.is_symlink()
session=sessions[0];metadata_path=workspace/'.git/entire-sessions'/f'{session}.json'
metadata_bytes=metadata_path.read_bytes();metadata=json.loads(metadata_bytes)
assert metadata['phase']=='ended' and metadata['session_id']==session and metadata['worktree_path']==str(workspace)
transcript_path=Path(metadata['transcript_path']);assert transcript_path.is_relative_to(profile/'sessions') and not transcript_path.is_symlink()
target_manifest=Path(result['target']['capture']['uri']);target_manifest_bytes=target_manifest.read_bytes()
assert sha(target_manifest_bytes)==result['target']['capture']['sha256']
assert result['target']['target_path']!=str(workspace)
out=judgment/'retention/late-capture-01';out.mkdir(parents=True,exist_ok=False)
for name in ['content','inventories','native','skills','commands']: (out/name).mkdir()
(out/'dispatch-at-stop.json').write_bytes(dispatch_bytes)
(out/'native-result-at-stop.json').write_bytes(result_bytes)
(out/'native/entire-session.json').write_bytes(metadata_bytes)
(out/'target-capture-manifest.json').write_bytes(target_manifest_bytes)
write(out/'capture-intent.json',{'schema':'coordinator-late-judge-preservation-v1','capture_started_at':now(),'judgment':identifier,'judge_finished_at':result['finished_at'],'launcher_finished_at':dispatch['finished_utc'],'source_attempt':str(attempt),'source_judge_workspace':str(workspace),'source_profile':str(profile),'source_transcript':str(transcript_path),'method':'Additive late coordinator copy after natural stop; not a launcher stop-time snapshot.','scope':'All attempt bytes including complete judgment output, Git metadata, failures, probes and replay artifacts. Isolated profile skills, native transcript and exact initial supplied skill targets are separate declared sources.','excluded_roots':[{'source':str(profile),'reason':'Entire profile not copied: authentication/history not required. Only exact session transcript, skills and public profile config are selected.'}],'frozen_helper_sha256':sha((HERE/'frozen_delivery_snapshot.py').read_bytes()),'script_sha256':sha(Path(__file__).read_bytes())})
roots=[];commands=[];omissions=[];errors=[]
def scan(source,destination=None):
    rows=[]
    def visit(parent,name,relative,physical,dest):
        before=os.stat(name,dir_fd=parent,follow_symlinks=False)
        row={'path':relative,'mode':stat.S_IMODE(before.st_mode),'source_signature':list(F._signature(before))}
        if F._credential_path(physical):
            row.update(kind='omitted-credential');omissions.append({'source':str(physical),'reason':'Frozen capture known-credential exclusion'});rows.append(row);return
        if stat.S_ISDIR(before.st_mode):
            fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
            try:
                assert F._signature(before)==F._signature(os.fstat(fd)),str(physical)
                row['kind']='directory';rows.append(row)
                if dest is not None:dest.mkdir()
                for child in sorted(os.listdir(fd)):
                    visit(fd,child,child if relative=='.' else relative+'/'+child,physical/child,dest/child if dest is not None else None)
                assert F._signature(before)==F._signature(os.fstat(fd)),str(physical)
                if dest is not None:os.chmod(dest,row['mode'])
            finally:os.close(fd)
        elif stat.S_ISREG(before.st_mode):
            digest=F._read_file(parent,name,before,dest)
            row.update(kind='file',size=before.st_size,sha256=digest);rows.append(row)
            if dest is not None:os.chmod(dest,row['mode'])
        elif stat.S_ISLNK(before.st_mode):
            link=os.readlink(name,dir_fd=parent);row.update(kind='symlink',link_target=link,sha256=sha(os.fsencode(link)));rows.append(row)
            assert F._signature(before)==F._signature(os.stat(name,dir_fd=parent,follow_symlinks=False)),str(physical)
            if dest is not None:
                os.symlink(link,dest)
                if hasattr(os,'lchmod'):os.lchmod(dest,row['mode'])
        else:
            row.update(kind='unsupported');rows.append(row);errors.append({'source':str(physical),'reason':'Unsupported special file retained only as metadata'})
    descriptor=os.open(source.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:visit(descriptor,source.name,'.',source,destination)
    finally:os.close(descriptor)
    return rows

def content_index(rows):return [{k:v for k,v in row.items() if k!='source_signature'} for row in rows]
def preserve(label,source,destination,attribution):
    before=scan(source);write(out/'inventories'/f'{label}-before.json',{'source':str(source),'started_at':now(),'entries':before})
    destination.parent.mkdir(parents=True,exist_ok=True)
    copied=scan(source,destination);after=scan(source)
    write(out/'inventories'/f'{label}-after.json',{'source':str(source),'finished_at':now(),'entries':after})
    destination_rows=scan(destination)
    same=before==copied==after;exact=content_index(before)==content_index(destination_rows)
    receipt={'label':label,'source':str(source),'retained_as':str(destination.relative_to(out)),'attribution':attribution,'before_after_source_equal':same,'retained_content_modes_links_equal':exact,'entries':len(before),'files':sum(r['kind']=='file' for r in before),'bytes':sum(r.get('size',0) for r in before),'source_before_index_sha256':sha((out/'inventories'/f'{label}-before.json').read_bytes()),'source_after_index_sha256':sha((out/'inventories'/f'{label}-after.json').read_bytes())}
    roots.append((receipt,before,source));write(out/'source-captures.json',{'sources':[r[0] for r in roots]})
    assert same and exact,label
    return before

def read_git(cwd,arguments,label):
    env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',GIT_TERMINAL_PROMPT='0')
    for key in ('GIT_DIR','GIT_WORK_TREE','GIT_COMMON_DIR','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES','GIT_NAMESPACE'):env.pop(key,None)
    argv=['git','--no-optional-locks','--no-replace-objects','-c','core.hooksPath=/dev/null','-C',str(cwd),*arguments]
    p=subprocess.run(argv,env=env,capture_output=True)
    (out/'commands'/f'{label}.stdout').write_bytes(p.stdout);(out/'commands'/f'{label}.stderr').write_bytes(p.stderr)
    commands.append({'argv':argv,'environment':{'GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0'},'stdout':f'commands/{label}.stdout','stderr':f'commands/{label}.stderr','returncode':p.returncode})
    write(out/'commands.json',commands)
    assert p.returncode==0,label
    return p.stdout

def event_identity(data):
    meta=[];completed=[];final=0;types=Counter();child=[]
    for line_no,line in enumerate(data.splitlines(),1):
        r=json.loads(line);p=r.get('payload',{});item=p.get('item',{})
        if r.get('type')=='session_meta':meta.append({'id':p.get('id'),'cwd':p.get('cwd')})
        if r.get('type')=='event_msg' and p.get('type')=='task_complete':final+=1
        if r.get('type')=='event_msg' and p.get('type')=='item_completed':
            completed.append(p);types[item.get('type')]+=1
            if any(t in str(item.get('type','')).lower() for t in ('spawn','collab','subagent')):child.append({'line':line_no,'type':item.get('type'),'id':item.get('id')})
        if r.get('type')=='response_item' and p.get('type') in ('function_call','custom_tool_call'):
            code=str(p.get('name',''))+' '+str(p.get('input',p.get('arguments','')))
            if any(t in code for t in ('spawn_agent','spawn_agents','spawn_subagent','collaboration.','functions.spawn')):child.append({'line':line_no,'type':'call_requires_review','name':p.get('name')})
    return {'metadata':meta,'session_and_cwd_match':any(m['id']==session and m['cwd']==str(workspace) for m in meta),'completed_item_events':len(completed),'task_complete_events':final,'completed_item_types':dict(types),'child_spawn_evidence':child},completed

summary={'judgment':identifier,'verified':False,'preservation_verified':False}
try:
    attempt_rows=preserve('complete-attempt',attempt,out/'content/attempt-01','Complete original completed judge attempt and output tree; late coordinator preservation')
    profile_rows=preserve('profile-skills',profile/'skills',out/'content/profile-skills','Availability only; initial catalog and runtime additions are distinct from installation/use')
    preserve('public-profile-config',profile/'config.toml',out/'content/profile-config.toml','Launcher public profile settings; authentication store excluded')
    preserve('raw-native-transcript',transcript_path,out/'native/native-transcript.jsonl','Exact native source bytes for this ended session')
    preflight=json.loads((out/'content/attempt-01/native/prompt-preflight.json').read_bytes());catalog=preflight['advertised_skill_catalog']
    skill_entries=[];supplied=[]
    for row in profile_rows:
        relative=Path(row['path'])
        if row['kind']=='file' and relative.name=='SKILL.md':
            source=profile/'skills'/relative;initial=[c for c in catalog if c['path']==str(source) and c.get('sha256')==row['sha256']]
            skill_entries.append({'source':str(source),'retained_as':str((out/'content/profile-skills'/relative).relative_to(out)),'sha256':row['sha256'],'initial_catalog_entry':initial[0] if initial else None,'initial_catalog_absence_does_not_establish_judge_installation':not bool(initial)})
        if row['kind']=='symlink' and len(relative.parts)==1:
            target=Path(row['link_target'])
            assert relative.name in ('assess-alignment-with-stamped-principles','stamped-conventions') and target.is_absolute() and target.name==relative.name
            assert not target.is_symlink() and target.parent.name=='skills'
            source_root=target.parent.parent
            source_pin=read_git(source_root,['rev-parse','HEAD'],f'assessment-source-{relative.name}').decode().strip()
            assert source_pin==result['assessment_pin']['source_commit']
            skill_tree=read_git(source_root,['ls-tree','HEAD','skills'],f'assessment-skills-tree-{relative.name}').decode().strip()
            skills_pin=read_git(target.parent,['rev-parse','HEAD'],f'assessment-skills-head-{relative.name}').decode().strip()
            if skill_tree.startswith('160000 '):assert skill_tree.split()[2]==skills_pin
            target_rows=preserve('supplied-'+relative.name,target,out/'content/supplied-skills'/relative.name,'Supplemental late bytes of the initial supplied assessor skill directory; no judge credit. Repository HEAD pin is recorded separately; ignored or generated bytes are not thereby claimed as pinned tracked content.')
            ep=next(r for r in target_rows if r['path']=='SKILL.md' and r['kind']=='file');initial=[c for c in catalog if c['path']==str(target/'SKILL.md') and c.get('sha256')==ep['sha256']];assert initial
            supplied.append({'profile_link':row,'source':str(target),'assessment_source_commit':source_pin,'skills_commit':skills_pin,'pin_scope':'Repository HEAD identity; full late directory bytes are independently hashed, including any ignored/generated files','full_directory_index':target_rows})
            skill_entries.append({'source':str(profile/'skills'/relative/'SKILL.md'),'retained_as':str(Path('content/supplied-skills')/relative/'SKILL.md'),'sha256':ep['sha256'],'initial_catalog_entry':initial[0],'attribution':'initial supplied assessor guidance'})
    workspace_relative=workspace.relative_to(attempt)
    workspace_skill_entries=[]
    for row in attempt_rows:
        p=Path(row['path'])
        if row['kind']=='file' and p.name=='SKILL.md' and p.is_relative_to(workspace_relative):workspace_skill_entries.append({'source':str(attempt/p),'retained_as':str(Path('content/attempt-01')/p),'sha256':row['sha256']})
    write(out/'skills/availability.json',{'scope':'Complete literal profile skill index, separate initial supplied link targets, and all workspace SKILL.md entrypoints. Availability does not establish installation, instruction reading, application, grading, or effect.','initial_catalog':catalog,'profile_directory_index':profile_rows,'profile_entrypoints':skill_entries,'supplied_targets':supplied,'workspace_entrypoints':workspace_skill_entries})
    captured_workspace=out/'content/attempt-01'/workspace_relative
    actual_head=read_git(captured_workspace,['rev-parse','HEAD'],'judge-head').decode().strip()
    refs=read_git(captured_workspace,['for-each-ref','--format=%(refname) %(objectname)','refs/heads/entire','refs/entire/checkpoints'],'entire-refs').decode().splitlines()
    raw=(out/'native/native-transcript.jsonl').read_bytes();native_identity,native_events=event_identity(raw)
    assert native_identity['session_and_cwd_match'] and native_identity['completed_item_events']>0
    if result['returncode']==0:assert native_identity['task_complete_events']>0
    shadows=[];checkpoint_refs=[];differences=[]
    key=lambda e:(e.get('type'),e.get('thread_id'),e.get('turn_id'),e.get('item',{}).get('type'),e.get('item',{}).get('id'))
    for line in refs:
        ref,oid=line.split()
        if ref.startswith('refs/entire/checkpoints/'):
            checkpoint_refs.append({'ref':ref,'oid':oid});continue
        number=len(shadows);paths=read_git(captured_workspace,['ls-tree','-r','--name-only',oid],f'shadow-{number:02d}-paths').decode().splitlines();stored=[]
        prefix=f'.entire/metadata/{session}/'
        for p in paths:
            if not p.startswith(prefix):continue
            name=f'shadow-{number:02d}-'+p[len(prefix):].replace('/','_');data=read_git(captured_workspace,['show',f'{oid}:{p}'],name)
            (out/'native'/name).write_bytes(data);item={'git_path':p,'retained_as':'native/'+name,'sha256':sha(data),'size':len(data)}
            if p.endswith('full.jsonl'):
                ident,events=event_identity(data);item['identity']=ident
                item['completed_event_identity_sequence_matches']=list(map(key,events))==list(map(key,native_events))
                assert ident['session_and_cwd_match'] and item['completed_event_identity_sequence_matches']
                for i,(a,b) in enumerate(zip(native_events,events)):
                    if a==b:continue
                    ai=a.get('item',{});bi=b.get('item',{})
                    differences.append({'shadow_file':'native/'+name,'event_index':i,'item_type':ai.get('type'),'item_id':ai.get('id'),'differing_payload_keys':sorted(k for k in set(a)|set(b) if a.get(k)!=b.get(k)),'differing_item_keys':sorted(k for k in set(ai)|set(bi) if ai.get(k)!=bi.get(k)),'native_event_sha256':sha(json.dumps(a,sort_keys=True).encode()),'shadow_event_sha256':sha(json.dumps(b,sort_keys=True).encode())})
            stored.append(item)
        shadows.append({'ref':ref,'oid':oid,'session_files':stored})
    full=[f for s in shadows for f in s['session_files'] if 'identity' in f];assert full
    write(out/'native/verification.json',{'session_id':session,'source_workspace':str(workspace),'source_transcript':str(transcript_path),'native_identity':native_identity,'native_transcript_sha256':sha(raw),'native_transcript_bytes':len(raw),'metadata_sha256':sha(metadata_bytes),'judge_starting_commit':result['starting_commit'],'judge_actual_stopped_head':actual_head,'shadow_checkpoints':shadows,'local_checkpoint_refs':checkpoint_refs,'completed_event_payload_differences':differences,'hosted_publication':'Not verified or attempted. Exact original shadow and raw native bytes retained separately.'})
    final_checks=[]
    for receipt,before,source in roots:
        after=scan(source);equal=before==after
        final_checks.append({'label':receipt['label'],'source':str(source),'before_final_source_equal':equal});assert equal,receipt['label']
    assert (judgment/'dispatch.json').read_bytes()==dispatch_bytes and (attempt/'native/result.json').read_bytes()==result_bytes and metadata_path.read_bytes()==metadata_bytes
    assert target_manifest.read_bytes()==target_manifest_bytes
    write(out/'source-final-equality.json',{'verified_at':now(),'sources':final_checks,'dispatch_unchanged':True,'native_result_unchanged':True,'target_manifest_unchanged':True,'target_scope':'Target body not copied or traversed by this preservation. Launcher target_unchanged value retained separately; this check confirms the exact target manifest stayed unchanged.','launcher_target_unchanged':result.get('target_unchanged')})
    summary={'schema':'coordinator-late-judge-preservation-v1','judgment':identifier,'verified':not omissions and not errors and not native_identity['child_spawn_evidence'],'preservation_verified':not omissions and not errors and not native_identity['child_spawn_evidence'],'launcher_returncode':dispatch['returncode'],'native_returncode':result['returncode'],'launcher_target_unchanged':result.get('target_unchanged'),'launcher_target_validation_error':result.get('target_validation_error'),'capture_finished_at':now(),'judge_finished_at':result['finished_at'],'output':str(out),'source_attempt_entries':len(attempt_rows),'source_attempt_files':sum(r['kind']=='file' for r in attempt_rows),'source_attempt_bytes':sum(r.get('size',0) for r in attempt_rows),'native_bytes':len(raw),'completed_events':native_identity['completed_item_events'],'native_task_complete_events':native_identity['task_complete_events'],'shadow_transcripts':len(full),'shadow_task_complete_events':[f['identity']['task_complete_events'] for f in full],'payload_difference_events':len(differences),'profile_skill_entrypoints':len(skill_entries),'workspace_skill_entrypoints':len(workspace_skill_entries),'supplied_skill_target_directories':len(supplied),'child_spawn_evidence':native_identity['child_spawn_evidence'],'source_before_after_equal':True,'late_capture':True,'original_native_result_modified':False,'original_judge_workspace_modified':False,'preservation_modified_target':False,'scientific_or_stamped_grading_performed':False,'hosted_publication_verified':False,'omissions':omissions,'errors':errors,'limitation':'Preservation verification is independent of judgment validity. A bounded post-stop observation is not an atomic or stop-time filesystem snapshot. File contents were hashed/copied without reading report or grade prose into model context.'}
except Exception as exc:
    (out/'failure.txt').write_text(traceback.format_exc());summary.update(error=str(exc),capture_finished_at=now(),omissions=omissions,errors=errors)
finally:
    write(out/'verification.json',summary);write(out/'commands.json',commands)
    entries=scan(out)
    write(out/'manifest.json',{'schema':'coordinator-retention-manifest-v1','files':content_index(entries),'script_sha256':sha(Path(__file__).read_bytes()),'note':'Manifest excludes itself; all source retention and comparison failures are retained.'})
print(json.dumps(summary,indent=2))
raise SystemExit(0 if summary['verified'] else 1)

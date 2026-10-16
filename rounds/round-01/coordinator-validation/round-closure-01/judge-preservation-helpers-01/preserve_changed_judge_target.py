"""Preserve a stopped judge's copied target exactly as found and index its delta.
No Git invocation, cleanup, replay, validation repair, or scientific interpretation.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,traceback
sys.dont_write_bytecode=True
import capture_io as IO
base=Path(__file__).resolve().parent.parent;identifier=sys.argv[1];run=identifier.rsplit('-j',1)[0]
judgment=base/'runs'/run/'judgments'/identifier;attempt=judgment/'attempt-01'
sha=lambda d:hashlib.sha256(d).hexdigest()
write=lambda p,o:p.write_text(json.dumps(o,indent=2)+'\n')
now=lambda:datetime.now(timezone.utc).isoformat()
dispatch_bytes=(judgment/'dispatch.json').read_bytes();dispatch=json.loads(dispatch_bytes)
assert dispatch['status']=='launcher-finished' and isinstance(dispatch['returncode'],int) and dispatch['finished_utc']
result_bytes=(attempt/'native/result.json').read_bytes();result=json.loads(result_bytes)
assert result['role']=='judge' and result['finished_at'] and isinstance(result['returncode'],int)
manifest=Path(result['target']['capture']['uri']);source=manifest.parent
assert source==base/'judge-targets'/identifier and not source.is_symlink()
manifest_bytes=manifest.read_bytes();baseline=json.loads(manifest_bytes);assert sha(manifest_bytes)==result['target']['capture']['sha256']
original_manifest=Path(dispatch['argv'][dispatch['argv'].index('--delivery-capture')+1])
assert original_manifest==base/'runs'/run/'attempt-01/native/original-delivery/manifest.json'
original_bytes=original_manifest.read_bytes();assert original_bytes==manifest_bytes
out=judgment/'retention/target-as-found-01';out.mkdir(parents=True,exist_ok=False)
(out/'declared-target-manifest.json').write_bytes(manifest_bytes);(out/'original-worker-capture-manifest.json').write_bytes(original_bytes)
(out/'judge-native-result.json').write_bytes(result_bytes);(out/'judge-dispatch.json').write_bytes(dispatch_bytes)
summary={'judgment':identifier,'preservation_verified':False,'capture_started_at':now(),'source':str(source),'output':str(out),'judge_finished_at':result['finished_at'],'launcher_returncode':dispatch['returncode'],'native_returncode':result['returncode'],'launcher_target_unchanged':result.get('target_unchanged'),'launcher_target_validation_error':result.get('target_validation_error'),'scope':'Late additive copy of stopped judged target exactly as found; path/content delta is mechanical evidence only. Prior target changes are preserved, not repaired or assigned a scientific meaning.'}
try:
    before=IO.scan(source);write(out/'source-before.json',{'entries':before})
    copied=IO.scan(source,out/'copied-target');after=IO.scan(source);write(out/'source-after.json',{'entries':after})
    assert before==copied==after
    retained=IO.scan(out/'copied-target');assert IO.content_index(before)==IO.content_index(retained)
    actual={r['path']:r for r in before if r['path']!='.'}
    expected={r['path']:r for r in baseline['entries']}
    administrative={'manifest.json','content','content/external'}
    added=[IO.content_index([actual[p]])[0] for p in sorted(set(actual)-set(expected)-administrative)]
    missing=[expected[p] for p in sorted(set(expected)-set(actual))]
    modified=[]
    for p in sorted(set(expected)&set(actual)):
        a=actual[p];e=expected[p];keys=['kind','mode']
        if e['kind']=='file':keys+=['size','sha256']
        elif e['kind']=='symlink':keys+=['link_target','sha256']
        changed=[k for k in keys if a.get(k)!=e.get(k)]
        if changed:modified.append({'path':p,'changed_fields':changed,'baseline':e,'as_found':IO.content_index([a])[0]})
    delta={'baseline_manifest_sha256':sha(manifest_bytes),'baseline_manifest_source':str(manifest),'original_worker_capture_manifest_source':str(original_manifest),'baseline_manifest_bytes_identical_to_original_worker_capture_manifest':True,'as_found_source':str(source),'as_found_copy':'copied-target','baseline_entry_count':len(expected),'as_found_entry_count':len(actual),'added':added,'missing':missing,'modified':modified}
    write(out/'manifest-to-as-found-delta.json',delta)
    final=IO.scan(source);assert before==final
    assert manifest.read_bytes()==manifest_bytes and original_manifest.read_bytes()==original_bytes and (attempt/'native/result.json').read_bytes()==result_bytes and (judgment/'dispatch.json').read_bytes()==dispatch_bytes
    summary.update(preservation_verified=not IO.omissions and not IO.errors,capture_finished_at=now(),source_before_copy_after_final_equal=True,retained_content_modes_links_equal=True,source_entries=len(before),source_regular_files=sum(r['kind']=='file' for r in before),source_regular_bytes=sum(r.get('size',0) for r in before),added_paths=len(added),missing_paths=len(missing),modified_paths=len(modified),original_worker_capture_manifest_unchanged=True,judge_result_unchanged=True,target_modified_by_preservation=False,omissions=IO.omissions,errors=IO.errors)
except Exception as exc:
    (out/'failure.txt').write_text(traceback.format_exc());summary.update(error=str(exc),capture_finished_at=now(),omissions=IO.omissions,errors=IO.errors)
finally:
    write(out/'verification.json',summary)
    write(out/'manifest.json',{'files':IO.content_index(IO.scan(out)),'script_sha256':sha(Path(__file__).read_bytes()),'library_sha256':sha((Path(__file__).parent/'capture_io.py').read_bytes()),'note':'Manifest excludes itself; all failures and literal target bytes are retained.'})
print(json.dumps(summary,indent=2))
raise SystemExit(0 if summary['preservation_verified'] else 1)

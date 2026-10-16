"""Read-only independent integrity audit of an additive judge retention bundle."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,stat,sys
base=Path(__file__).resolve().parent.parent;identifier=sys.argv[1];run=identifier.rsplit('-j',1)[0]
root=base/'runs'/run/'judgments'/identifier/'retention/late-capture-01'
sha=lambda d:hashlib.sha256(d).hexdigest()
m=json.loads((root/'manifest.json').read_bytes());rows=m['files'];expected=set();counts={};total=0
for r in rows:
    p=root/r['path'];expected.add(r['path']);s=p.lstat();assert stat.S_IMODE(s.st_mode)==r['mode'],str(p)
    kind=r['kind'];counts[kind]=counts.get(kind,0)+1
    if kind=='file':assert p.is_file() and not p.is_symlink() and s.st_size==r['size'] and sha(p.read_bytes())==r['sha256'],str(p);total+=s.st_size
    elif kind=='directory':assert p.is_dir() and not p.is_symlink(),str(p)
    elif kind=='symlink':assert p.is_symlink() and os.readlink(p)==r['link_target'] and sha(os.fsencode(os.readlink(p)))==r['sha256'],str(p)
    else:raise ValueError(kind)
actual={'.'}|{str(p.relative_to(root)) for p in root.rglob('*') if str(p.relative_to(root))!='manifest.json'}
assert actual==expected,actual.symmetric_difference(expected)
v=json.loads((root/'verification.json').read_bytes());assert v['source_before_after_equal']
resolution_ref=None
if not v['verified']:
    assert not v['omissions'] and not v['errors'] and v['child_spawn_evidence']
    rp=root.parent/'child-call-resolution-01/resolution.json';data=rp.read_bytes();resolution=json.loads(data)
    assert resolution['broad_matches_resolved_as_non_invocations'] and resolution['original_verification_remains_false']
    assert [r['native_line'] for r in resolution['records']]==[r['line'] for r in v['child_spawn_evidence']]
    for key in ['original_preservation_verification','raw_transcript','native_identity_verification','session_metadata']:
        binding=resolution[key];assert sha(Path(binding['path']).read_bytes())==binding['sha256']
    resolution_ref={'path':str(rp),'size':len(data),'sha256':sha(data)}
checks=json.loads((root/'source-final-equality.json').read_bytes());assert all(r['before_final_source_equal'] for r in checks['sources'])
result={'audited_at':datetime.now(timezone.utc).isoformat(),'judgment':identifier,'capture_manifest':str(root/'manifest.json'),'capture_manifest_sha256':sha((root/'manifest.json').read_bytes()),'verified':True,'original_capture_verified':v['verified'],'child_match_resolution':resolution_ref,'entry_kinds':counts,'regular_file_bytes':total,'exact_retained_file_set':True,'source_before_after_checks':len(checks['sources']),'scientific_or_stamped_content_interpreted':False,'scope':'Independent artifact byte/mode/link integrity and retained source-equality checks. Any original broad-match failure remains unchanged and is bound to a separate literal-call resolution; no replay or judge launch.'}
out=root.parent/'late-capture-01.integrity-audit.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

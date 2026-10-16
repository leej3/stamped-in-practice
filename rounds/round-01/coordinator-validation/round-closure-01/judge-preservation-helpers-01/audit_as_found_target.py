"""Read-only independent integrity audit of an additive judge retention bundle."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,stat,sys
base=Path(__file__).resolve().parent.parent;identifier=sys.argv[1];run=identifier.rsplit('-j',1)[0]
root=base/'runs'/run/'judgments'/identifier/'retention/target-as-found-01'
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
v=json.loads((root/'verification.json').read_bytes());assert v['preservation_verified'] and v['source_before_copy_after_final_equal']
checks={'sources':[v]};assert v['retained_content_modes_links_equal']
result={'audited_at':datetime.now(timezone.utc).isoformat(),'judgment':identifier,'capture_manifest':str(root/'manifest.json'),'capture_manifest_sha256':sha((root/'manifest.json').read_bytes()),'verified':True,'entry_kinds':counts,'regular_file_bytes':total,'exact_retained_file_set':True,'source_before_after_checks':len(checks['sources']),'scientific_or_stamped_content_interpreted':False,'scope':'Artifact byte/mode/link integrity and retained equality receipts only; no replay or judge launch.'}
out=root.parent/'target-as-found-01.integrity-audit.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

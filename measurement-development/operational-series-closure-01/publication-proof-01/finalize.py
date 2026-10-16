from pathlib import Path
import sys,json,shutil
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1');R=B/'operational-synthesis-proof-package-01';src=B/'operational-synthesis-publication-01'
sys.path.insert(0,str(B/'operational-support-tools-01'));import package as method
m=json.loads((R/'manifest.json').read_text());assert method.inventory(src,['fresh-git'])==m['entries'];v=method.verify(R/'evidence.tar.gz',m['entries']);assert method.inventory(src,['fresh-git'])==m['entries']
for p in [Path(method.__file__),Path(method.safe.__file__)]:shutil.copy2(p,R/p.name)
v.update(source_unchanged=True,archive_sha256=method.sha(R/'evidence.tar.gz'),archive_bytes=(R/'evidence.tar.gz').stat().st_size,manifest_sha256=method.sha(R/'manifest.json'),prior_attempt={'script':'archive.py','failure':'shutil.SameFileError while copying its own already-present source after successful archive verification; no source or archive overwrite','recovery':'separate finalize.py reverified complete existing archive and source before/after, copied remaining helper methods'},publication_status='payload upload pending Hub recovery; Git/Entire facts scoped separately')
(R/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))

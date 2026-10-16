#!/usr/bin/env python3
"""Restore only the 54 fixed participant COPE maps listed in input/sources.json."""
from pathlib import Path
import concurrent.futures, hashlib, json, urllib.request
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'input'/'sources.json').read_text())['files']
items=[(ROOT/key,meta) for key,meta in manifest.items() if key.startswith('data/')]
if len(items)!=54:
    raise RuntimeError(f'Expected 54 participant maps, found {len(items)}')
def restore(item):
    path,meta=item
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink() and not path.exists():
        path.unlink()  # replace a broken git-annex pointer in the supplied workspace
    if path.exists():
        raw=path.read_bytes()
        if len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256']:
            return path.name,'verified existing'
    request=urllib.request.Request(meta['url'],headers={'User-Agent':'NARPS-group-analysis/1.0'})
    with urllib.request.urlopen(request,timeout=90) as response:
        raw=response.read()
    digest=hashlib.sha256(raw).hexdigest()
    if len(raw)!=meta['bytes'] or digest!=meta['sha256']:
        raise ValueError(f'Checksum/size mismatch for {path.name}')
    path.write_bytes(raw)
    return path.name,'downloaded and verified'
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    for name,status in pool.map(restore,items): print(status,name)

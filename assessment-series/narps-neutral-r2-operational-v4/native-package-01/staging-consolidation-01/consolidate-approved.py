from pathlib import Path
import json, hashlib, shutil, datetime, os
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1')
R=B/'storage-accounting-02'; proposal=json.loads((R/'proposal.json').read_text())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
archive=Path(proposal['verified_archive']['path']); manifest=archive.parent/'manifest.json'; verification=archive.parent/'verification.json'
v=json.loads(verification.read_text()); entries=json.loads(manifest.read_text())['entries']
assert v['verified'] and v['all_member_bytes_modes_links_verified'] and v['sources_before_after_equal']
assert archive.is_file() and archive.stat().st_size==v['archive_bytes']==13856638499
assert proposal['verified_archive']['sha256']==v['archive_sha256'] in archive.resolve().name
assert digest(manifest)==v['manifest_sha256']==proposal['verified_archive']['manifest_sha256']
rows=proposal['paths']; assert len(rows)==32 and len({x['path'] for x in rows})==32
root=B/'round-02-native-retention-01/judgments'
checks=[]
for row in rows:
 p=Path(row['path']); assert p.parent.parent.parent==root and p.name=='content' and p.parent.name=='late-capture-01'
 assert p.is_dir() and not p.is_symlink() and p.resolve()==p
 prefix=row['archive_prefix']; assert prefix=='native-retention/'+str(p.relative_to(B/'round-02-native-retention-01'))+'/'
 selected=[e for e in entries if e['path'].startswith(prefix)]
 assert len(selected)==row['entries'] and sum(e.get('size',0) for e in selected if e['type']=='file')==row['regular_bytes']
 mapping=p.parent/'source-captures.json'; sources=json.loads(mapping.read_text())['sources']
 assert all(Path(s['source']).exists() or Path(s['source']).is_symlink() for s in sources)
 assert (p.parent/'native').is_dir()
 checks.append({'path':str(p),'archive_member_prefix':prefix,'regular_bytes':row['regular_bytes'],'source_mapping':str(mapping),'source_mapping_sha256':digest(mapping),'original_source_paths':[s['source'] for s in sources], 'restore_command':['tar','-xzf',str(archive),'-C','<empty-restore-directory>',prefix.rstrip('/')], 'restore_note':'Extract exact prefix in an empty directory, verify against manifest.json, then copy the restored content subtree to this path if needed.'})
receipt={'started_at':now(),'authorization':'Root explicitly authorized ONLY the 32 exact paths in proposal.json on 2026-10-16; no other cleanup, cache deletion, annex drops or source movement.','proposal_sha256':digest(R/'proposal.json'),'archive':str(archive),'local_annex_object':str(archive.resolve()),'archive_sha256':v['archive_sha256'],'archive_bytes':v['archive_bytes'],'archive_availability':'Existing all-member verification plus current local annex object path, size and manifest digest confirmed before removal. No new remote claim.','verification_path':str(verification),'verification_sha256':digest(verification),'manifest_sha256':v['manifest_sha256'],'free_bytes_before':shutil.disk_usage(B).free,'paths':checks,'removed':[]}
(R/'consolidation-start.json').write_text(json.dumps(receipt,indent=2)+'\n')
with (R/'removals.jsonl').open('x') as log:
 for row in checks:
  p=Path(row['path']); shutil.rmtree(p); assert not p.exists()
  item={'path':str(p),'archive_member_prefix':row['archive_member_prefix'],'removed_at':now()}; receipt['removed'].append(item); log.write(json.dumps(item)+'\n'); log.flush(); os.fsync(log.fileno())
assert archive.is_file() and archive.stat().st_size==v['archive_bytes']
for row in checks:
 assert Path(row['source_mapping']).is_file() and digest(Path(row['source_mapping']))==row['source_mapping_sha256']
 assert (Path(row['path']).parent/'native').is_dir()
 assert all(Path(p).exists() or Path(p).is_symlink() for p in row['original_source_paths'])
receipt.update(completed_at=now(),removed_count=len(receipt['removed']),free_bytes_after=shutil.disk_usage(B).free,original_sources_and_metadata_retained=True,remote_payload_status='pending; not checked',verified=True)
(R/'consolidation-result.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ['verified','removed_count','free_bytes_before','free_bytes_after','archive_sha256','remote_payload_status']}))

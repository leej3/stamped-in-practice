from pathlib import Path
import json,hashlib,shutil,datetime,os,stat
B=Path('/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1'); R=B/'storage-accounting-02'
r=json.loads((R/'consolidation-start.json').read_text()); a=Path(r['archive']); assert a.is_file() and a.stat().st_size==r['archive_bytes']; assert r['archive_sha256'] in a.resolve().name
assert not (R/'consolidation-result.json').exists(); assert len(r['paths'])==32
r['continuation']='Attempt01 stopped on read-only copied annex object directories. Attempt02 only makes real directories inside each approved duplicate subtree owner-writable before deleting that same subtree. Symlink targets and original source files are not changed.'
r['removed']=[]; r['directory_mode_adjustments']=[]
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
with (R/'removals-02.jsonl').open('x') as log:
 for row in r['paths']:
  p=Path(row['path']); assert p.name=='content' and p.parent.name=='late-capture-01' and p.parent.parent.parent==B/'round-02-native-retention-01/judgments'; assert p.is_dir() and not p.is_symlink()
  changed=0
  for base,dirs,files in os.walk(p,topdown=True,followlinks=False):
   q=Path(base); assert not q.is_symlink(); mode=stat.S_IMODE(q.stat().st_mode)
   if mode&0o700!=0o700: os.chmod(q,mode|0o700,follow_symlinks=False); changed+=1
   dirs[:]=[d for d in dirs if not (q/d).is_symlink()]
  shutil.rmtree(p); assert not p.exists()
  item={'path':str(p),'archive_member_prefix':row['archive_member_prefix'],'removed_at':now(),'copied_directory_modes_adjusted':changed}; r['removed'].append(item); log.write(json.dumps(item)+'\n'); log.flush(); os.fsync(log.fileno())
for row in r['paths']:
 p=Path(row['source_mapping']); assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==row['source_mapping_sha256']
 assert (Path(row['path']).parent/'native').is_dir()
 assert all(Path(x).exists() or Path(x).is_symlink() for x in row['original_source_paths'])
assert a.is_file() and a.stat().st_size==r['archive_bytes']
r.update(completed_at=now(),removed_count=len(r['removed']),free_bytes_after=shutil.disk_usage(B).free,original_sources_and_metadata_retained=True,remote_payload_status='pending; not checked',verified=True)
(R/'consolidation-result.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['verified','removed_count','free_bytes_before','free_bytes_after','archive_sha256','remote_payload_status']}))

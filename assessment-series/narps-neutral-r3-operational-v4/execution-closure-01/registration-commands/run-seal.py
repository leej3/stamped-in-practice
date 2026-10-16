from pathlib import Path
import json,subprocess,datetime
g=Path(__file__).resolve().parent
r=json.loads((g/'seal-command-planned.json').read_bytes())
r['started_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=subprocess.run(r['argv'],cwd=r['cwd'],capture_output=True,text=True)
r.update(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(g/'seal-command.json').write_text(json.dumps(r,indent=2)+'\n')
print(p.stdout);print(p.stderr);raise SystemExit(p.returncode)

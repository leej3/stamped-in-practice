"""Index actual child-agent call evidence only in retained stopped parent logs.
An absent match is not a global claim that child sessions cannot exist.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib,json,sys
base=Path(__file__).resolve().parent.parent;wave=base/f'round-01-wave-{int(sys.argv[1]):02d}'
gate_bytes=(wave/'stop-validation.json').read_bytes();rows=json.loads(gate_bytes)['runs']
assert len(rows)==3 and all(r['returncode']==0 and r['finished_at'] and r['validation']['capture_status']=='complete' for r in rows)
sha=lambda data:hashlib.sha256(data).hexdigest()
results=[]
for row in rows:
    root=base/'runs'/row['run']/'retention/native-capture-01'
    transcript=(root/'native-transcript.jsonl').read_bytes();metadata=(root/'entire-session.json').read_bytes();meta=json.loads(metadata)
    assert meta['phase']=='ended' and meta['session_id']==row['native_session_ids'][0]
    types=Counter();names=Counter();evidence=[]
    for line_no,line in enumerate(transcript.splitlines(),1):
        record=json.loads(line);payload=record.get('payload',{});item=payload.get('item',{})
        if record.get('type')=='event_msg' and payload.get('type')=='item_completed':
            kind=str(item.get('type',''));types[kind]+=1
            if any(token in kind.lower() for token in ('collab','spawn','subagent')):
                evidence.append({'line':line_no,'kind':'completed_child_tool_item','item_type':kind,'item_id':item.get('id'),'item_sha256':sha(json.dumps(item,sort_keys=True).encode())})
        if record.get('type')=='response_item' and payload.get('type') in ('function_call','custom_tool_call'):
            name=str(payload.get('name',''));names[name]+=1
            code=str(payload.get('input',payload.get('arguments','')))
            tokens=[t for t in ('spawn_agent','spawn_agents','spawn_subagent','collaboration.','functions.spawn') if t in name or t in code]
            if tokens:evidence.append({'line':line_no,'kind':'call_name_or_code_requires_review','name':name,'tokens':tokens,'call_id':payload.get('call_id'),'payload_sha256':sha(json.dumps(payload,sort_keys=True).encode())})
    results.append({'run':row['run'],'session_id':meta['session_id'],'retained_transcript':str(root/'native-transcript.jsonl'),'transcript_sha256':sha(transcript),'retained_session_metadata':str(root/'entire-session.json'),'session_metadata_sha256':sha(metadata),'metadata_subagent_inventory_complete':meta.get('subagent_inventory_complete'),'completed_item_types':dict(types),'response_tool_names':dict(names),'child_spawn_evidence':evidence,'child_log_retention_required_by_observed_evidence':bool(evidence)})
output=Path(__file__).resolve().parent/f'wave-{int(sys.argv[1]):02d}-child-agent-evidence.json'
assert not output.exists(),str(output)
output.write_text(json.dumps({'verified_at':datetime.now(timezone.utc).isoformat(),'stop_validation_sha256':sha(gate_bytes),'scope':'Stopped retained parent transcript call/event evidence only. No active sessions opened, no child or review launched, no inference from skill availability or prose. Any positive match requires child identity and completed-status verification before child-log retention.','runs':results},indent=2)+'\n')
(Path(__file__).resolve().parent/f'wave-{int(sys.argv[1]):02d}-child-agent-evidence-manifest.json').write_text(json.dumps({'files':[{'path':str(p),'sha256':sha(p.read_bytes()),'size':p.stat().st_size} for p in [Path(__file__).resolve(),output]]},indent=2)+'\n')
print(json.dumps({'wave':wave.name,'runs':[{'run':r['run'],'child_spawn_evidence_count':len(r['child_spawn_evidence']),'metadata_subagent_inventory_complete':r['metadata_subagent_inventory_complete']} for r in results]},indent=2))
raise SystemExit(2 if any(r['child_spawn_evidence'] for r in results) else 0)

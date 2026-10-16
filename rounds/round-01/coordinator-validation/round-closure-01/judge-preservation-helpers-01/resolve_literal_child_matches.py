"""Resolve broad child-call substring matches only when they are Python literals.
Reads retained stopped evidence; does not execute retained commands or read grades.
Original failed verification remains unchanged.
"""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;identifier=sys.argv[1];run=identifier.rsplit('-j',1)[0]
r=BASE/'runs'/run/'judgments'/identifier/'retention';capture=r/'late-capture-01';out=r/'child-call-resolution-01';out.mkdir(exist_ok=False)
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):
 b=p.read_bytes();return {'path':str(p),'size':len(b),'sha256':sha(b)}
v=json.loads((capture/'verification.json').read_bytes());assert not v['verified'] and v['source_before_after_equal'] and not v['omissions'] and not v['errors']
raw=(capture/'native/native-transcript.jsonl').read_bytes();lines=raw.splitlines();meta=json.loads((capture/'native/entire-session.json').read_bytes());assert meta['phase']=='ended' and meta['subagent_inventory_complete'] is True
nv=json.loads((capture/'native/verification.json').read_bytes());assert nv['native_transcript_sha256']==sha(raw)
assert not any(any(t in k.lower() for t in ('collab','spawn','subagent')) for k in nv['native_identity']['completed_item_types'])
records=[];pattern=re.compile(rb'spawn_agents?|spawn_subagent|collaboration\.|functions\.spawn')
for flagged in v['child_spawn_evidence']:
 assert flagged['type']=='call_requires_review'
 n=flagged['line'];payload=json.loads(lines[n-1])['payload'];assert payload['type']=='custom_tool_call' and payload['name']=='exec'
 code=payload['input'];calls=re.findall(r'tools\.([A-Za-z0-9_]+)\s*\(',code);assert calls==['exec_command']
 match=re.search(r'\bcmd\s*:\s*',code);assert match
 command,end=json.JSONDecoder().raw_decode(code[match.end():]);assert isinstance(command,str)
 rest=code[:match.end()]+code[match.end()+end:];assert not pattern.search(rest.encode())
 command_lines=command.splitlines(keepends=True);literal_ranges=[];blocks=[];offset=0;i=0
 while i<len(command_lines):
  line=command_lines[i]
  if "<<'PY'" in line:
   assert re.fullmatch(r"python(?:3)? - <<'PY'\s*",line)
   closing=next(j for j in range(i+1,len(command_lines)) if command_lines[j].strip()=='PY')
   body=''.join(command_lines[i+1:closing]);tree=ast.parse(body);body_start=sum(len(x.encode()) for x in command_lines[:i+1]);body_lines=body.splitlines(keepends=True)
   starts=[0]
   for text in body_lines:starts.append(starts[-1]+len(text.encode()))
   constant_count=0
   for node in ast.walk(tree):
    if isinstance(node,ast.Constant) and isinstance(node.value,str):
     begin=body_start+starts[node.lineno-1]+node.col_offset;finish=body_start+starts[node.end_lineno-1]+node.end_col_offset
     literal_ranges.append((begin,finish,sha(node.value.encode())));constant_count+=1
   blocks.append({'shell_line':i+1,'python_syntax_parsed':True,'string_literal_count':constant_count,'source_sha256':sha(body.encode())});i=closing
  i+=1
 observed=[]
 for m in pattern.finditer(command.encode()):
  containers=[x for x in literal_ranges if x[0]<=m.start() and m.end()<=x[1]];assert containers,(n,m.start())
  observed.append({'token':m.group().decode(),'command_byte_offset':m.start(),'classification':'Python string literal, not a called function identifier','literal_sha256':containers[0][2]})
 assert observed
 records.append({'native_line':n,'payload_sha256':sha(json.dumps(payload,sort_keys=True).encode()),'input_sha256':sha(code.encode()),'native_tool_name':payload['name'],'wrapper_tool_calls':calls,'command_sha256':sha(command.encode()),'parsed_heredocs':blocks,'matches':observed})
receipt={'schema':'child-call-literal-resolution-v1','recorded_at':datetime.now(timezone.utc).isoformat(),'judgment':identifier,'original_preservation_verification':ref(capture/'verification.json'),'raw_transcript':ref(capture/'native/native-transcript.jsonl'),'native_identity_verification':ref(capture/'native/verification.json'),'session_metadata':ref(capture/'native/entire-session.json'),'original_verification_remains_false':True,'broad_matches_resolved_as_non_invocations':True,'observed_native_child_invocations':0,'missing_child_logs_identified':False,'metadata_subagent_inventory_complete':meta['subagent_inventory_complete'],'records':records,'scope':'Every flagged substring occurs in a parsed Python string literal carried by an exec_command wrapper; completed event types contain no child/collaboration invocation. This resolves the broad substring trigger only. It neither executes commands nor interprets scientific/report content, and does not prove that no unobserved external process could exist.','source_files_modified':False,'script':ref(Path(__file__))}
if identifier=='narps-neutral-r1-15-j01':receipt['preliminary_parser_failures_retained']=[{'native_lines':[159,168],'attempt':'Decode entire JavaScript object as JSON','error':'JSONDecodeError: Expecting property name enclosed in double quotes','resolution':'Decode only the cmd string literal; JavaScript object uses unquoted keys.'},{'native_lines':[168],'attempt':'Parse all command lines between first/last PY delimiters as a single Python block','error':'SyntaxError: invalid syntax (<unknown>, line 20)','resolution':'Parse each Python heredoc separately; shell command contains multiple blocks.'}]
(out/'resolution.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'manifest.json').write_text(json.dumps({'files':[ref(out/'resolution.json')],'script':ref(Path(__file__))},indent=2)+'\n')
print(json.dumps({'resolution':ref(out/'resolution.json'),'flagged_native_lines':[x['native_line'] for x in records],'all_matches_are_literals':True},indent=2))

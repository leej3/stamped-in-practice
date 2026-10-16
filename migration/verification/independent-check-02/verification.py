"""Fresh published dataset retrieval and comparison reconstruction proof."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time

out = Path(__file__).parent / 'independent-check-02'
out.mkdir(exist_ok=False)
shutil.copyfile(__file__, out / 'verification.py')
ds = out / 'recipient'
px = ['pixi', 'run', '--locked', '--manifest-path', '/Users/johnlee/code/CON/stamped-in-practice/pixi.toml']
commands = []
def run(label, argv, cwd=None):
    start=time.monotonic()
    r=subprocess.run(argv,cwd=cwd or out,capture_output=True,timeout=2400,
                     env=dict(os.environ,GIT_TERMINAL_PROMPT='0'))
    stem=f'{len(commands)+1:03d}-{label}'
    for suffix,data in [('stdout',r.stdout),('stderr',r.stderr)]:
        (out/(stem+'.'+suffix)).write_bytes(data)
    commands.append(dict(label=label,argv=argv,cwd=str(cwd or out),returncode=r.returncode,
                         elapsed_seconds=time.monotonic()-start,stdout=stem+'.stdout',stderr=stem+'.stderr'))
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    assert r.returncode == 0, f'{label}: {r.returncode}; see {stem}.stderr'
    return r.stdout
def git(root,label,*args):return run(label,['git','-C',str(root),*args])
def annex(root,label,*args):return run(label,px+['git','-C',str(root),'annex',*args])
def route(root):
    git(root,'annex-metadata','fetch','--no-tags','origin','git-annex:refs/remotes/origin/git-annex')
    git(root,'ignore-github','config','remote.origin.annex-ignore','true')
    annex(root,'annex-init','init','independent migration verification')
    git(root,'content-route','remote','add','con-hub','https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git')
    git(root,'content-endpoint','config','remote.con-hub.annexurl','annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp')
    annex(root,'merge-annex','merge')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def references(v,base):
    if isinstance(v,dict):
        if isinstance(v.get('path'),str) and 'sha256' in v:
            yield (Path(os.path.abspath(base/v['path'])),v['sha256'])
        for x in v.values():yield from references(x,base)
    elif isinstance(v,list):
        for x in v:yield from references(x,base)

result={'success':False,'dataset_commit':'a0bfc5f4b958b7c10192d00ab8b9fc9885201b33',
        'scope':'Fresh SSH Git and authorized con-hub retrieval; no scientific analyses or judgments repeated.'}
try:
    run('clone',['git','clone','--depth','1','--single-branch','--branch','codex/iteration-narps-v1',
                 'git@github.com:leej3/stamped-in-practice.git',str(ds)])
    assert git(ds,'head','rev-parse','HEAD').decode().strip()==result['dataset_commit']
    assert not (ds/'.git/objects/info/alternates').exists()
    assert not (ds/'study/.git').exists() and not (ds/'assessment/.git').exists()
    result['initial_submodules_uninitialized']=True
    rows=json.loads((ds/'migration/original-manifest.json').read_text())['records']
    annexed=[r for r in rows if 'annex_key' in r]
    assert all(not (ds/r['path']).exists() for r in annexed)
    route(ds)
    annex(ds,'get-original-payloads','get','--from','con-hub','--jobs','3','--',*[r['path'] for r in annexed])
    run('complete-original-proof',px+['python',str(ds/'migration/verify_original.py'),'--dataset',str(ds),
                                     '--output',str(out/'original-files-verification.json')])
    result['original_paths_verified']=len(rows);result['original_annex_payloads_freshly_retrieved']=len(annexed)
    git(ds,'install-selected-resources','submodule','update','--init','--depth','1','--','study','assessment')
    assert not any((ds/'study/results'/f'narps-r1-{n:02d}'/'.git').exists() for n in range(1,13))
    result['study_results_initially_uninitialized']=True
    names=[f'results/narps-r1-{n:02d}' for n in range(1,13)]
    git(ds/'study','install-selected-results','submodule','update','--init','--depth','1','--',*names)
    refs=[]
    for name in ['index.json','disposition.json','reported-scientific-estimates.json']:
        refs.extend(references(json.loads((ds/'replay'/name).read_text()),ds/'replay'))
    for n in range(1,13):
        root=ds/'study/results'/f'narps-r1-{n:02d}'
        route(root)
        paths=sorted({str(path.relative_to(root)) for path,h in refs if path.is_relative_to(root) and not path.exists()})
        if paths:annex(root,f'get-indexed-evidence-{n:02d}','get','--from','con-hub','--jobs','3','--',*paths)
    for path,expected in refs:assert sha(path)==expected,str(path)
    result['exact_reference_hashes_verified']=len(refs)
    original=json.loads((ds/'procedure.json').read_text())
    # The original response contract is also checked by the retained aggregator.
    # Read the actual pin from the immutable original seal, not the short label.
    def pins(v):
        if isinstance(v,dict):
            for x in v.values():yield from pins(x)
        elif isinstance(v,list):
            for x in v:yield from pins(x)
        elif isinstance(v,str) and v.startswith('0208f825') and len(v)==40:yield v
    original_pin=next(pins(original))
    git(ds/'assessment','original-assessor-contract','fetch','--depth','1','origin',original_pin)
    shutil.copyfile(ds/'synthesis/analysis/validated-environment.lock',ds/'synthesis/analysis/pixi.lock')
    replaypx=['pixi','run','--locked','--manifest-path',str(ds/'synthesis/analysis/pixi.toml')]
    run('reconstruct-comparison',replaypx+['python',str(ds/'synthesis/analysis/aggregate_comparison.py'),
        '--allocation',str(ds/'allocation.json'),'--index',str(ds/'replay/index.json'),
        '--disposition',str(ds/'replay/disposition.json'),'--assessor',str(ds/'assessment'),
        '--assessment-pin',str(ds/'synthesis/analysis/assessment-version.json'),
        '--assessment-procedure-sha256','5dfdfa07f8e9488a79bbddb27df75a76ad5484941ac1d0efb197b0b3126994b5',
        '--output',str(out/'aggregate')])
    tables=[]
    for source in sorted((ds/'synthesis/aggregate').glob('*.jsonl')):
        new=out/'aggregate'/source.name
        assert new.read_bytes()==source.read_bytes(),source.name
        tables.append({'path':source.name,'sha256':sha(new)})
    result['exact_reconstructed_tables']=tables
    run('reconstruct-figures',replaypx+['python',str(ds/'synthesis/analysis/round1_figures.py'),
        '--tables',str(out/'aggregate'),'--estimates',str(ds/'replay/reported-scientific-estimates.json'),
        '--output',str(out/'figures')])
    result['success']=True
except Exception as e:result['error']=f'{type(e).__name__}: {e}'
finally:
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['success'] else 1)

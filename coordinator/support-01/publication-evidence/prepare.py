from pathlib import Path
import hashlib, json, shutil, subprocess

ROOT = Path(__file__).resolve().parent
B = ROOT.parent
MAIN = Path('/Users/johnlee/code/CON/stamped-in-practice')
RUN = 'narps-neutral-r1-03'
PACKAGE = B/'support-package-r1-03-01'
REPO = ROOT/'publisher'
ORIGIN = 'https://github.com/leej3/stamped-in-practice.git'
BRANCH = 'codex/'+RUN+'-support-01'
PIXI = ['pixi','run','--manifest-path',str(MAIN/'pixi.toml'),'--locked']
commands = []

def save(path, value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def run(argv, cwd=ROOT, allow=False):
    argv=list(map(str,argv))
    p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True)
    commands.append({'argv':argv,'cwd':str(cwd),'returncode':p.returncode,
                     'stdout':p.stdout,'stderr':p.stderr})
    save(ROOT/'prepare-commands.json',commands)
    if not allow:p.check_returncode()
    return p

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def copy(source, target):
    assert source.is_file() and not source.is_symlink(),source
    digest=sha(source); target.parent.mkdir(parents=True,exist_ok=True)
    assert not target.exists(),target
    shutil.copy2(source,target)
    assert sha(target)==sha(source)==digest

def prepare():
    assert not REPO.exists()
    package_index=json.loads((PACKAGE/'proof-index.json').read_bytes())
    assert package_index['status']=='verified' and package_index['original_source_unchanged']
    for entry in package_index['files']:
        source=PACKAGE/entry['path']
        assert sha(source)==entry['sha256'] and source.stat().st_size==entry['size']
    verification=json.loads((PACKAGE/'verification.json').read_bytes())
    assert verification['verified'] and verification['source_before_copy_after_equal']
    published=json.loads((MAIN/'studies/narps/neutral-retention-publications.json').read_bytes())
    canonical=next(row['commit'] for row in published['runs'] if row['run_id']==RUN)
    base=json.loads((PACKAGE/'config.json').read_bytes())['native_publication_base']
    native_proofs=[json.loads(p.read_bytes()) for p in (B/'runs'/RUN/'judgments').glob('*/retention/native-publication-01/proof-publication-01/result.json')]
    assert native_proofs and all(p['verified'] and p['source_files_unchanged'] for p in native_proofs)
    assert base in [p['proof_commit'] for p in native_proofs]
    run(['git','init','--initial-branch',BRANCH,REPO])
    run(['git','remote','add','origin',ORIGIN],REPO)
    run(['git','remote','set-url','--push','origin','git@github.com:leej3/stamped-in-practice.git'],REPO)
    run(['git','fetch','--no-tags','origin',base],REPO)
    run(['git','reset','--hard','FETCH_HEAD'],REPO)
    assert not (REPO/'.git/objects/info/alternates').exists()
    run(['git','merge-base','--is-ancestor',canonical,base],REPO)
    for proof in native_proofs:run(['git','merge-base','--is-ancestor',proof['proof_commit'],base],REPO)
    assert run(['git','rev-parse','HEAD'],REPO).stdout.strip()==base
    run(['git','config','remote.origin.annex-ignore','true'],REPO)
    host=json.loads(Path('/Users/johnlee/.config/stamped-in-practice/launch-neutral.json').read_bytes())
    run(PIXI+['git','annex','init',RUN+' coordinator support publisher'],REPO)
    run(['git','remote','add',host['annex_remote'],host['annex_git_url']],REPO)
    run(['git','config','remote.'+host['annex_remote']+'.annexurl',host['annex_url']],REPO)
    dst=REPO/'coordinator/support-01'
    for entry in package_index['files']:
        copy(PACKAGE/entry['path'],dst/entry['path'])
    copy(PACKAGE/'proof-index.json',dst/'proof-index.json')
    for name in ['NEUTRAL-SCOPE-OVERRIDE.json','original-delivery-reconstruction.json',
                 'path-mapping.json','package-manifest.json','package-plan.json']:
        copy(PACKAGE/'staging'/name,dst/'scope'/name)
    assignments=json.loads((B/'dataset/rounds/round-01/plan.json').read_bytes())['assigned_judgments']
    judges=[entry['judgment'] for entry in assignments if entry['run']==RUN]
    assert judges
    for judge in judges:
        extraction=B/'judgment-extractions'/judge
        assert (extraction/'canonical-report.md').is_file() and (extraction/'canonical-response.json').is_file()
        for source in sorted(extraction.iterdir()):
            if source.is_file():copy(source,REPO/'coordinator/judgments'/judge/'assessment'/source.name)
    (dst/'README.md').write_text('''# Complete support for run 03

This coordinator archive preserves the completed research and independent
assessment evidence, including raw native captures, execution logs, available
skills, failed attempts and the complete closed judgment workspace.
The [support archive](support.tar.gz), [member inventory](support-archive-inventory.json)
and [verification](verification.json) bind the retained bytes.

The [neutral scope record](scope/NEUTRAL-SCOPE-OVERRIDE.json) is authoritative
for original-delivery identity. The [path mapping](scope/path-mapping.json)
accounts for every source entry. The two omitted copies are represented by the
independently retrieved original-delivery archive; its exact key and
reconstruction instructions remain in the [reconstruction record](scope/original-delivery-reconstruction.json).

The [judge report](../judgments/narps-neutral-r1-03-j01/assessment/canonical-report.md)
and [structured response](../judgments/narps-neutral-r1-03-j01/assessment/canonical-response.json)
are exact copies. Coordinator extraction and binding records accompany them.
This publication does not create worker-practice credit or change the original
delivery, raw judgment or formal admission criteria.

For large files, follow the [artifact retrieval guide](https://github.com/leej3/stamped-in-practice/blob/main/RETRIEVAL.md).
Native hosted attachment is a separate publication record; the full raw native
transcript is retained here regardless of hosted processing or visibility.
''')
    with (dst/'README.md').open('a') as stream:
        stream.write('\n## Assigned assessment records\n\n')
        for judge in judges:
            stream.write('- ['+judge+'](../judgments/'+judge+'/assessment/canonical-report.md)\n')
        stream.write('\nReport-local probe and replay links refer to the complete archived judgment workspace.\n')
    nav=REPO/'coordinator/README.md'
    with nav.open('a') as stream:
        stream.write('\n## Completed support and assessment\n\n'
                     'See the [complete support archive and evidence index](support-01/README.md), '
                     'including the exact independent report and structured response.\n')
    attrs=REPO/'.gitattributes'
    with attrs.open('a') as stream:
        stream.write('\n# Exact coordinator support archive; readable evidence remains in Git.\n'
                     'coordinator/support-01/** annex.largefiles=nothing\n'
                     'coordinator/support-01/support.tar.gz annex.largefiles=anything annex.backend=SHA256E\n')
    format_argv=PIXI+['pre-commit','run','--config',str(MAIN/'.pre-commit-config.yaml'),
                      'snapper','--files','coordinator/README.md','coordinator/support-01/README.md']
    if run(format_argv,REPO,allow=True).returncode:run(format_argv,REPO)
    manifest=[]
    for top in [dst]+[REPO/'coordinator/judgments'/j/'assessment' for j in judges]:
        for p in sorted(top.rglob('*')):
            if p.is_file():manifest.append({'path':str(p.relative_to(REPO)),
                                           'sha256':sha(p),'bytes':p.stat().st_size})
    save(dst/'publication-files.json',manifest)
    run(PIXI+['git','annex','add','--force-large','--backend=SHA256E','--',
              'coordinator/support-01/support.tar.gz'],REPO)
    archive=package_index['archive']
    key=f"SHA256E-s{archive['size']}--{archive['sha256']}.tar.gz"
    assert run(PIXI+['git','annex','lookupkey','coordinator/support-01/support.tar.gz'],REPO).stdout.strip()==key
    run(['git','add','.gitattributes','coordinator'],REPO)
    paths=run(['git','diff','--cached','--name-only'],REPO).stdout.splitlines()
    assert paths and all(p=='.gitattributes' or p.startswith('coordinator/') for p in paths)
    run(['git','diff','--cached','--check','--','.gitattributes','coordinator/README.md','coordinator/support-01/README.md'],REPO)
    trailers=run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'],REPO).stdout.strip()
    message=('chore(retention): publish run 03 complete support evidence\n\n'
             'Preserve the verified support archive and exact readable judgment.\n'
             'Keep original delivery, worker history and scientific files unchanged.\n'
             'Record coordinator preservation and extraction separately.\n\n'+trailers+'\n')
    (ROOT/'commit-message.txt').write_text(message)
    run(['git','commit','-F',ROOT/'commit-message.txt'],REPO)
    head=run(['git','rev-parse','HEAD'],REPO).stdout.strip()
    assert run(['git','rev-parse','HEAD^'],REPO).stdout.strip()==base
    changed=run(['git','diff','--name-only',base,head],REPO).stdout.splitlines()
    assert changed==paths
    assert run(['git','rev-parse',head+':input'],REPO).stdout==run(['git','rev-parse',base+':input'],REPO).stdout
    assert run(['git','status','--porcelain'],REPO).stdout.strip()==''
    result={'run_id':RUN,'base':base,'commit':head,'branch':BRANCH,'publisher':str(REPO),
            'archive_path':'coordinator/support-01/support.tar.gz','archive_key':key,
            'archive_sha256':archive['sha256'],'archive_bytes':archive['size'],
            'publication_manifest_sha256':sha(dst/'publication-files.json'),
            'scope':'Coordinator support only; original worker delivery and judgments unchanged.'}
    save(ROOT/'prepared.json',result);print(json.dumps(result))

try:prepare()
except BaseException as exc:
    save(ROOT/'failure.json',{'type':type(exc).__name__,'error':str(exc)})
    raise

# Package coordinator evidence

After a worker and its assigned judgments stop, copy their coordinator records into a new staging directory:

```sh
pixi run python scripts/package_retention.py --plan /path/run-plan.json --output /path/coordinator-retention
```

The plan names the evidence root, original worker stop receipt and exact scientific result:

```json
{
  "version": 1,
  "source": "/path/to/run-evidence",
  "worker_stop": "launch/native/worker-end-state.json",
  "scientific_result": "FULL_GIT_OBJECT_ID",
  "exclude": []
}
```

All files and failed attempts are included unless explicitly excluded.
The package preserves receipt bytes, relative paths and original absolute provenance; native results, canonical responses, reports and output-binding manifests remain directly addressable under `evidence/`.
It includes its plan, packager source, per-file hashes and source-to-package mapping.
It verifies the copied tree and checks that the source inventory did not change during the copy.
Existing destinations are rejected; partial failed packages remain for diagnosis.
Run only on stopped evidence, since two inventory checks are not a filesystem snapshot.

For a reconstructable recipient clone, restored archive copy or dependency cache, add an explicit exclusion:

```json
{
  "path": "retention/recipient-check-01/recipient",
  "reason": "Independent retrieval completed; retained receipts identify every object",
  "reconstruct_from": {
    "repository": "git@github.com:OWNER/REPOSITORY.git",
    "result_commit": "FULL_GIT_OBJECT_ID",
    "annex_access": "Declared recipient route in the retained retrieval receipt"
  },
  "evidence": ["retention/recipient-check-01/result.json"]
}
```

The coordinator reviews whether the evidence actually justifies reconstruction.
The tool requires that proof files remain in the package; it does not infer exclusions or grade their sufficiency.
Do not exclude unique replay attempts, coordinator interventions, failed commands, installed-skill archives or environment snapshots.
Existing byte-exact archives and their restore proofs can justify omitting a duplicate restored tree.
Symlinks retain their exact link text, including missing annex pointers in failed attempts; this does not assert that their targets are available.

The scientific result stays fixed.
Its original stop receipt inventories code, data, figures and requested duct files; ignored skills and final environment snapshots need separate retained evidence.
The packager neither fetches nor republishes those scientific artifacts.
After verifying independent scientific retrieval and this package, add the package in a later experiment retention commit, annex large files, publish payloads and register that retention commit.
Keep the recorded scientific result as the judgment target.
No frozen launcher, assessor, Pixi manifest or runtime is changed by this packaging command.

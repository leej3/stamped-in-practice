# Migration verification

The original iteration contains 711 tracked paths and 37 unique annex keys.
All original ordinary blobs and payload bytes remain unchanged; annex symlinks were regenerated at the new directory depth.
The complete [original manifest](original-manifest.json), [prepublication check](prepublication-verification.json) and preserved full-history branch identify the source.

The [independent dataset check](verification/independent-check-03/result-complete.json) used a fresh GitHub recipient and fetched all 37 original annex payloads from the authorized content route.
It verified every original path and 321 current evidence references, restored the retained Pixi environment, and regenerated all eighteen comparison tables and four PNG figures.
Tables differ only in the declared evidence-path prefix; scientific outcomes, evidence hashes and PNG bytes match.
The original failed checks remain alongside their successful completion receipts: a verifier resolved annex symlinks too early, a GitHub SSH fetch timed out, and an initial table comparison did not allow the declared path relocation.
These were coordinator verification errors, not changes to worker findings.

The [fresh public parent check](verification/parent-fresh-check-01/result-complete.json) cloned main shallowly over HTTPS with all four root submodules uninitialized.
It installed only this iteration, fetched one figure, then installed its study and one result to fetch a scientific NIfTI payload.
Eleven experiment modules and the unrelated root study/assessor modules stayed uninitialized.
Initial selectors assumed an annexed PNG, but this worker stored PNGs in ordinary Git and its annexed maps as unlocked pointers; both failed selectors are preserved.
Native annex inventory and exact payload hashes established the successful retrieval.

The [retention manifest](verification/retention-manifest.json) inventories all copied proof files.
Only reconstructable recipient caches are omitted; commands, failed attempts, environment restoration evidence, reconstructed tables/figures and source identities remain.
Access was authorized through the current host's configured annex route; public Git retrieval does not establish anonymous annex access or portability to another host.

# Repository navigation review

Repository: `/Users/johnlee/code/CON/stamped-in-practice`
Root revision: `34fbe9d951a1abd83d18775d51eb0bfb32ac8e57`
Scope: fresh-visitor organization review beginning at `README.md`; no research or treatment grading. No repository sources or published outputs changed.

The root communicates the question, four assistance conditions and research-to-skill-improvement process clearly (`README.md:5–29`). It separates the completed development comparison, sealed neutral comparison and completed first neutral round, with the 21/32 measurement count and link to current status (`README.md:58–64`). The status and viability disposition clearly hold further research pending a bounded measurement decision; a candidate requires a live synthetic trial and explicit registration decision before adoption (`iterations/narps-neutral-v1/STATUS.md:10–16`; `rounds/round-01/synthesis/viability.md:12–19`, relative to that iteration). A fresh coordinator can determine this next boundary without treating historical preparation or development as formal neutral outcomes.

## Confirmed navigation defect

- **Minor: the retrieval guide overstates one navigation layout.** `RETRIEVAL.md:30–31` permits substituting another experiment and states that each experiment has `coordinator/README.md`. The published historical `studies/narps/results/narps-r1-01` at `6c0c006580890a030c572d488f584a91ce0d611d` has no such file; its guide is `coordinator/retention-01/README.md`, confirmed in the Git tree. `studies/narps/README.md:53–55` already explains the older layout. Scope the retrieval instruction to current neutral experiments and point historical readers to their retention guide. This is a navigation mismatch, not evidence of missing retention content.

## Evidence routes and boundaries

| Need | Working navigation route |
| --- | --- |
| Study task and fixed inputs | Root location table (`README.md:40–42`) → `studies/narps/README.md:3–10,13–39` → `input/`, scientific rubric and retrieval checks |
| Original worker object | Study guide (`studies/narps/README.md:43–49`) → exact experiment publication tree → `coordinator/delivery-01/delivery.tar.gz`, manifest and original HEAD/capture identities |
| Frozen assessments | Root `assessment-version.json` and `assessment/` pin; neutral registration and procedure remain unchanged; synthesis links original report/response extraction and assigned judgment receipts |
| Skill changes | Root development comparison link → `iterations/narps-v1/DATASET.md:6` → `skill-reflection/README.md` → research-guidance and separate assessor trial records, exact source commits and retained archives |
| Complete execution evidence | Root retrieval guide → experiment coordinator guide; current synthesis (`rounds/round-01/synthesis/README.md:131–133`) → `EXPERIMENTS.md` exact commits; `REPRODUCE.md:40–43` locates complete underlying attempts/native logs in support archives |

Git tree inspection confirms five root gitlinks (`skills`, `assessment`, two iterations, one study), and the study contains 36 result gitlinks: 24 neutral and 12 development. The neutral iteration independently pins study, skills and assessment. These boundaries keep result datasets and their bulk payloads out of a default nonrecursive root checkout. No submodules were initialized by this review.

The development README retains old active-sounding registration text, but the root deliberately links `DATASET.md`, which identifies that README and synthesis as original historical records and supplies current replay navigation (`iterations/narps-v1/DATASET.md:3–4,13–18`). This is disclosed history, not an additional defect.

## Verification limits

- All 52 local Markdown link targets in the initially selected navigation documents had filesystem entries. This checks entries, not annex payload availability or validity of scientific evidence. Intentionally historical links in the later-read development synthesis were not included in this count.
- The README's three exact development/registration/synthesis URL targets and RETRIEVAL's exact run20 retrieval-record target were verified as local Git objects using their containing repositories; HTTP reachability was not tested.
- The run20 coordinator guide was read from locally available linked commit `b1e9d12ec5158036eadfb6ff06a7f8b240ef80e0`. The later publication `17a648a191814a227abc90c052a1bd083e14449c` is an uninitialized gitlink and its object was unavailable to the root Git object store. A failed lookup there is **not** a broken-link finding.
- Live branch URLs, external skill/source repositories, annex downloads, archive completeness, and independent retrieval claims were not revalidated. No archive payload, prior agent messages or host service data was opened.
- `inspected-files.json` records exact SHA-256 hashes for all 26 working-tree files and the one Git-object file read, plus the inspected repository HEAD identities.

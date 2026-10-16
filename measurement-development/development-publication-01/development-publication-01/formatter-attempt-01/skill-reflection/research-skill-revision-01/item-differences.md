# Item-level changes

| Item | Before | After | Evidence-based explanation |
|---|---|---|---|
| must/006 | unmet | partial | New verification runs link commands, source snapshots, pins and output hashes; the original supplied-output runtime remains unknown. |
| must/013 | met | partial | The original requirements.txt is versioned; the new exact lock and interpreter specification are delivered but still uncommitted. |
| must/014 | unmet | partial | README.md gives the executable lock-update and replay process; no dependency-update instance is committed in history yet. |
| must/015 | unmet | met | The delivered lock pins thirteen runtime packages and .python-version pins the interpreter; a fresh installation reproduced the numeric summary exactly. |
| should/002 | not-checked | partial | The documented workflow completed twice and a repeat-before-handoff policy is stated; regular testing over time is not established. |
| should/004 | not-checked | met | A new isolated venv installed the exact lock and completed the workflow with exact numeric agreement on this same host. |
| should/006 | not-checked | partial | One fresh reconstitution of the pinned verification environment succeeded; a policy exists but no regular reconstitution history is established. |
| should/008 | unmet | partial | README.md gives the executable lock-update and replay process; no dependency-update instance is committed in history yet. |
| may/002 | unmet | met | README.md maps input, computation, environment, supplied outputs and verification snapshots and explains their composition. |
| may/005 | partial | met | The README provides a contents map, installation/use steps and interpretation of the run records; HANDOFF.md lists changes and remaining limits. |

All other item statuses are unchanged.
MUST partial is not satisfied; no overall score is computed.
The new exact lock being uncommitted changes must/013 from met to partial; that is reported rather than hidden.

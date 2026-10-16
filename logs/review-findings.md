# Independent review findings and responses

The fresh review examined task commit `c001a6c019558a79e74cb4cd1e333dc15435a472`, before the final support audit and follow-up changes.

| Finding | Response |
| --- | --- |
| The task commit did not itself contain `pixi.lock`. | This is intentional under the requested policy: retain the lock as ordinary Git on `codex/env-narps-r1-12-20261015`, one commit above the final task commit. The branch will be refreshed against the final task commit before release. |
| Union support could treat exact zeros from unsupported map regions as observed effects. | Audited support: 53,034 voxels were nonzero in some but not all maps. Revised the primary mask to the 198,029-voxel intersection of nonzero support, documented the exact-zero ambiguity, reran inference and independently checked the mask size. |
| The spatial figure missed the corrected posterior peak and its title was clipped. | Recentered orthogonal cuts at the peak coordinates (−26, −102, −3.6) and shortened the title. The final rendering was visually inspected. |

The reviewer’s independent statistical assessment was that the sign-flip max-t workflow, effect interpretation, and conclusion were coherent, conditional on the sign-flip symmetry assumption.

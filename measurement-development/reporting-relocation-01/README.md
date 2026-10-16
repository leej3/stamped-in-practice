# Relocated reporting evidence

Reporting revision `8de6636ff1bad6b2ec51b0baa30cbb670b3e89da` adds an explicit hash-checked map for retained evidence moved away from the original host paths.
Main integration `2f641a9134b9740a3ee859d8f2bd2d7e487fe957` has identical source bytes.
The running judges, frozen source, criteria and raw receipts remain unchanged.

The retained validation compared all 36 exported tables with the frozen reader: they matched exactly while 804 original paths were denied and 464 copied source files remained unchanged.
All 246 relevant tests passed, with one skip.
The complete validation evidence is packaged and verified locally with no exclusions; its bulk archive upload and independent remote retrieval remain pending because of the Hub connection failure.
The adjacent manifest and verification record identify every archived byte.
Do not treat this pending archive as remotely retrieved.

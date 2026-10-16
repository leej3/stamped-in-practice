# Pending archive transfers

The original run12 support upload failed during Hub remote discovery with a proxy error.
A bounded recovery using the previously verified remote UUID reached the annex HTTP transport but timed out connecting.
Run17 sent its archive bytes but ultimately returned failure with HTTP502 errors; sent-byte progress is not proof of storage.
It ended before the coordinator’s guarded interruption attempt sent any signal.
An independent unauthenticated endpoint check also timed out with no received bytes.

All commands and failures are retained here.
Original local captures and verified local archives remain available, and the formal assessment queue continues.
Their remote archive publication and fresh retrieval are pending; the ordinary Git content refs do not establish payload availability.
No worker, assessed target or judgment was repaired or replaced because of these transport failures.

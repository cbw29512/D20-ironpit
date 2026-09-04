from __future__ import annotations

# Explicit opt-in list for data-first native monsters. The catalog still runs
# the complete SRD source audit before any entry can become RAW READY.
NATIVE_READY_BY_NAME: dict[str, str] = {
    "Hill Giant": "srd-hill-giant",
    "Spy": "srd-spy",
}

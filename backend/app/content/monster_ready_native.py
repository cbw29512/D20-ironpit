from __future__ import annotations

# Explicit opt-in list for data-first native monsters. The catalog still runs
# the complete SRD source audit before any entry can become RAW READY.
NATIVE_READY_BY_NAME: dict[str, str] = {
    "Hill Giant": "srd-hill-giant",
    "Spy": "srd-spy",
    "Hell Hound": "srd-hell-hound",
    "Black Dragon Wyrmling": "srd-black-dragon-wyrmling",
    "Young Black Dragon": "srd-young-black-dragon",
    "Blue Dragon Wyrmling": "srd-blue-dragon-wyrmling",
    "Young Blue Dragon": "srd-young-blue-dragon",
    "Green Dragon Wyrmling": "srd-green-dragon-wyrmling",
    "Young Green Dragon": "srd-young-green-dragon",
    "Red Dragon Wyrmling": "srd-red-dragon-wyrmling",
    "Young Red Dragon": "srd-young-red-dragon",
    "White Dragon Wyrmling": "srd-white-dragon-wyrmling",
    "Young White Dragon": "srd-young-white-dragon",
}

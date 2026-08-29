from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "backend" / "app" / "content" / "data" / "srd_5_2_1_monsters.json"
DESTINATION = ROOT / "frontend" / "data" / "srd_5_2_1_monsters.json"


def main() -> None:
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != 328:
        raise RuntimeError("Static SRD monster catalog must contain exactly 328 records.")
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, DESTINATION)
    print(f"Prepared {len(rows)} SRD monsters for static browser delivery.")


if __name__ == "__main__":
    main()

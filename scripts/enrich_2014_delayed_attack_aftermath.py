from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
_DELAYED_CORPSE_AFTERMATH = re.compile(
    r"(?:A [^.]+ slain by this attack|If [^.]+ dies from this attack),?\s+.*?"
    r"(?:\d+d\d+|\d+)\s+(?:hours?|days?)\s+later.*$",
    re.I | re.S,
)


def strip_delayed_aftermath(text: str) -> str:
    return _DELAYED_CORPSE_AFTERMATH.sub(" ", text).strip(" .,;")


def main() -> int:
    parser = argparse.ArgumentParser(description="Exclude delayed post-combat attack aftermath from 2014 arena blockers.")
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8")); cleaned = 0
        for monster in catalog:
            for attack in monster.get("attacks", []):
                residual = attack.get("unsupported_text") or ""
                if not residual: continue
                remaining = strip_delayed_aftermath(residual)
                if remaining == residual: continue
                attack["unsupported_text"] = remaining or None
                attack["source_complete"] = not remaining
                cleaned += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"excluded {cleaned} delayed post-combat attack aftermath rider(s)")
        return 0
    except Exception as exc:
        logger.exception("2014 delayed attack aftermath enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

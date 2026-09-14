from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from import_2014_attack_details import parse_on_hit_control

logger = logging.getLogger(__name__)
_CREATURE_GRAPPLE_PREFIX = re.compile(
    r"^If the target is a creature,?\s*(?=(?:the target|it) is grappled\b)", re.I,
)


def parse_plain_creature_grapple(text: str) -> tuple[dict | None, bool, str]:
    """Normalize generic creature-only grapple wording into the shared grapple parser."""
    normalized = _CREATURE_GRAPPLE_PREFIX.sub("", text.strip(), count=1)
    if normalized == text.strip():
        return None, False, text
    return parse_on_hit_control(normalized)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich plain creature-qualified 2014 grapple riders.")
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        enriched = 0
        for monster in catalog:
            for attack in monster.get("attacks", []):
                text = attack.get("unsupported_text") or ""
                if not text:
                    continue
                control, forbid, residual = parse_plain_creature_grapple(text)
                if control is None or residual.strip(" .,;"):
                    continue
                existing = attack.get("control_effect")
                if existing is not None and existing != control:
                    continue
                attack["control_effect"] = control
                attack["forbid_target_grappled_by_self"] = forbid
                attack["unsupported_text"] = None
                attack["source_complete"] = True
                enriched += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {enriched} plain creature grapple rider(s)")
        return 0
    except Exception as exc:
        logger.exception("2014 plain creature grapple enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

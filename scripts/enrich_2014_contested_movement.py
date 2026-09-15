from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
_CONTEST_PULL = re.compile(
    r"If the target is a (Tiny|Small|Medium|Large|Huge|Gargantuan) or smaller creature, "
    r"it must succeed on a (Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) contest "
    r"against the ([A-Za-z][A-Za-z '\-/]+?) or be pulled up to (\d+) feet toward the \3\.?",
    re.I,
)


def parse_contested_movement(text: str) -> tuple[dict | None, str]:
    match = _CONTEST_PULL.search(text)
    if match is None:
        return None, text
    size, ability, _source_name, distance = match.groups()
    effect = {
        "source_ability": ability.lower(),
        "target_ability": ability.lower(),
        "max_target_size": size.lower(),
        "distance_ft": int(distance),
        "direction": "toward_source",
    }
    residual = f"{text[:match.start()]} {text[match.end():]}".strip(" .,;")
    return effect, residual


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich 2014 opposed-check forced movement attack riders.")
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8")); parsed = 0
        for monster in catalog:
            for attack in monster.get("attacks", []):
                if attack.get("source_complete", True):
                    continue
                effect, residual = parse_contested_movement(attack.get("unsupported_text") or "")
                if effect is None:
                    continue
                attack["on_hit_contested_movement"] = effect
                attack["unsupported_text"] = residual or None
                attack["source_complete"] = not residual
                parsed += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed} contested movement attack rider(s)")
        return 0
    except Exception as exc:
        logger.exception("2014 contested movement enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

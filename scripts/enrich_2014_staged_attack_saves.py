from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
_STAGED_PETRIFICATION = re.compile(
    r"(?:the target|it) must succeed on a DC (?P<dc>\d+) (?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) "
    r"saving throw against being magically petrified\.\s*On a failed save, (?:the target|the creature|it) begins to turn to stone and is restrained\.\s*"
    r"(?:It|The target|The creature) must repeat the saving throw at the end of its next turn\.\s*On a success, the effect ends\.\s*"
    r"On a failure, (?:the target|the creature|it) is petrified for (?P<amount>\d+) (?P<unit>hours?|minutes?)\.?'?",
    re.I | re.S,
)


def parse_staged_petrification(text: str) -> dict | None:
    match = _STAGED_PETRIFICATION.fullmatch(text.strip(" .,;"))
    if match is None:
        return None
    return {
        "save_ability": match.group("ability").lower(),
        "dc": int(match.group("dc")),
        "condition_id": "restrained",
        "repeat_save_timing": "target_turn_end",
        "repeat_save_failure_condition_id": "petrified",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich staged 2014 on-hit save riders from preserved source residuals.")
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        parsed = 0
        for monster in catalog:
            for attack in monster.get("attacks", []):
                if attack.get("source_complete", True):
                    continue
                residual = attack.get("unsupported_text") or ""
                effect = parse_staged_petrification(residual)
                if effect is None:
                    continue
                attack["on_hit_save_effect"] = effect
                attack["source_complete"] = True
                attack["unsupported_text"] = None
                parsed += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed} staged petrification attack riders")
        return 0
    except Exception as exc:
        logger.exception("2014 staged attack-save enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

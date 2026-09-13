from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
_ABILITY = r"(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)"
_MAX_HP_REDUCTION_PATTERNS = (
    re.compile(
        rf"(?:The target|It) must succeed on a DC (\d+) {_ABILITY} saving throw or "
        r"(?:its|the target's) hit point maximum is reduced by an amount equal to the damage taken\.\s*"
        r"This reduction lasts until (?:the target|the creature|it) finishes a long rest\.\s*"
        r"(?:The target|It) dies if (?:this effect|the reduction) reduces (?:its|the target's) hit point maximum to 0\.?",
        re.I,
    ),
    re.compile(
        rf"If the target is a creature, it must succeed on a DC (\d+) {_ABILITY} saving throw or "
        r"have its hit point maximum reduced by an amount equal to the damage taken\.\s*"
        r"The target dies if this attack reduces its hit point maximum to 0\.\s*"
        r"The reduction lasts until removed by the greater restoration spell or other magic\.?",
        re.I,
    ),
)
_DIRECT_DRAIN = re.compile(
    r"The target's hit point maximum is reduced by an amount equal to the ([a-z]+) damage taken, "
    r"and the [a-z /-]+ regains hit points equal to that amount\.\s*"
    r"The reduction lasts until the target finishes a long rest\.\s*"
    r"The target dies if this effect reduces its hit point maximum to 0\.?(?:\s*"
    r"A humanoid slain in this way.*?under the [a-z /-]+ control)?",
    re.I,
)


def _match_reduction(text: str):
    return next((match for pattern in _MAX_HP_REDUCTION_PATTERNS if (match := pattern.search(text))), None)


def _consume(attack: dict, residual: str, match: re.Match[str]) -> None:
    remainder = (residual[:match.start()] + " " + residual[match.end():]).strip(" .,;")
    attack["unsupported_text"] = remainder or None
    attack["source_complete"] = not remainder


def enrich_attack(attack: dict) -> bool:
    try:
        residual = attack.get("unsupported_text") or ""
        direct = _DIRECT_DRAIN.search(residual)
        if direct is not None:
            attack["max_hp_drain"] = {
                "damage_type": direct.group(1).lower(),
                "heal_attacker": True,
                "zero_max_hp_kills": True,
            }
            _consume(attack, residual, direct)
            return True
        match = _match_reduction(residual)
        if match is None:
            return False
        if attack.get("on_hit_save_effect") is not None:
            raise ValueError(f"Attack {attack.get('id')} already has an on-hit save effect.")
        dc, ability = match.groups()
        attack["on_hit_save_effect"] = {
            "save_ability": ability.lower(),
            "dc": int(dc),
            "max_hp_reduction_equals_damage_taken": True,
            "zero_max_hp_kills": True,
        }
        _consume(attack, residual, match)
        return True
    except Exception:
        logger.exception("Failed to enrich max-HP reduction attack %s.", attack.get("id"))
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Bind generic 2014 max-HP reduction attack riders.")
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8")); changed = 0
        for monster in catalog:
            for attack in monster.get("attacks", []):
                changed += int(enrich_attack(attack))
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {changed} max-HP reduction attack riders")
        return 0
    except Exception:
        logger.exception("2014 max-HP reduction enrichment failed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

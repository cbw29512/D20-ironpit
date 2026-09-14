from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
_CONDITIONS = "blinded|charmed|deafened|frightened|grappled|incapacitated|paralyzed|petrified|poisoned|prone|restrained|stunned|unconscious"
_REPLACEMENT_PATTERN = re.compile(
    rf"(?:and\s+)?the target must succeed on a DC (?P<dc>\d+) "
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw or be "
    rf"(?P<primary>{_CONDITIONS}) for (?P<base_amount>\d+) (?P<base_unit>minutes?|hours?)\.\s*"
    rf"If the saving throw fails by (?P<margin>\d+) or more, the target is instead (?P=primary) for "
    rf"\d+ \((?P<count>\d+)d(?P<size>\d+)\) (?P<replacement_unit>minutes?|hours?) and "
    rf"(?P<additional>{_CONDITIONS}) while (?P=primary) in this way\.?'?",
    re.I,
)
_SLEEP_POISON_PATTERN = re.compile(
    r"(?:and\s+)?the target must succeed on a DC (?P<dc>\d+) "
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw or "
    r"be(?:come)? poisoned for (?P<base_amount>\d+) (?P<base_unit>minutes?|hours?)\.\s*"
    r"If (?:(?:the saving throw fails by (?P<margin>\d+) or more)|(?:its saving throw result is (?P<max_result>\d+) or lower)), "
    r"(?:the poisoned target|the target) falls unconscious for the same duration, or until it takes damage or "
    r"another creature (?:uses|takes) an action to shake (?:it|the target) awake\.?'?",
    re.I,
)


def _rounds(amount: int, unit: str) -> int:
    return amount * (600 if unit.lower().startswith("hour") else 10)


def _replacement_effect(match: re.Match[str]) -> dict:
    return {
        "save_ability": match.group("ability").lower(),
        "dc": int(match.group("dc")),
        "condition_id": match.group("primary").lower(),
        "duration_rounds": _rounds(int(match.group("base_amount")), match.group("base_unit")),
        "failure_margin_escalation": {
            "margin": int(match.group("margin")),
            "additional_condition_ids": [match.group("additional").lower()],
            "replacement_duration_dice_count": int(match.group("count")),
            "replacement_duration_dice_size": int(match.group("size")),
            "replacement_duration_round_multiplier": _rounds(1, match.group("replacement_unit")),
        },
    }


def _sleep_poison_effect(match: re.Match[str]) -> dict | None:
    dc = int(match.group("dc"))
    margin = int(match.group("margin")) if match.group("margin") else dc - int(match.group("max_result"))
    if margin < 1:
        return None
    return {
        "save_ability": match.group("ability").lower(),
        "dc": dc,
        "condition_id": "poisoned",
        "duration_rounds": _rounds(int(match.group("base_amount")), match.group("base_unit")),
        "failure_margin_escalation": {
            "margin": margin,
            "additional_condition_ids": ["unconscious"],
            "ends_on_damage": True,
            "allowed_removal_action_ids": ["wake-sleeper"],
        },
    }


def parse_failure_margin_save(text: str) -> dict | None:
    cleaned = text.strip(" .,;")
    replacement = _REPLACEMENT_PATTERN.fullmatch(cleaned)
    if replacement is not None:
        return _replacement_effect(replacement)
    sleep_poison = _SLEEP_POISON_PATTERN.fullmatch(cleaned)
    return _sleep_poison_effect(sleep_poison) if sleep_poison is not None else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich failed-save margin attack riders in the 2014 catalog.")
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8")); parsed = 0
        for monster in catalog:
            for attack in monster.get("attacks", []):
                if attack.get("source_complete", True): continue
                effect = parse_failure_margin_save(attack.get("unsupported_text") or "")
                if effect is None: continue
                attack["on_hit_save_effect"] = effect; attack["source_complete"] = True; attack["unsupported_text"] = None; parsed += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed} failed-save margin attack rider(s)")
        return 0
    except Exception as exc:
        logger.exception("2014 failure-margin save enrichment failed: %s", exc); return 1


if __name__ == "__main__": raise SystemExit(main())

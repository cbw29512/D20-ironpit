from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
_INFERNAL_WOUND = re.compile(
    r"If the target is a creature other than an undead or a construct, it must succeed on a DC (\d+) Constitution saving throw or lose \d+ \((\d+)d(\d+)\) hit points at the start of each of its turns due to an infernal wound\.\s*"
    r"Each time the [^.]+ hits the wounded target with this attack, the damage dealt by the wound increases by \d+ \((\d+)d(\d+)\)\.\s*"
    r"Any creature can take an action to stanch the wound with a successful DC (\d+) Wisdom \(Medicine\) check\.\s*"
    r"The wound also closes if the target receives magical healing\.??",
    re.I,
)
_GRAPPLE_DAMAGE = re.compile(
    r"(?:the target|it)?\s*(?:and\s+)?takes \d+ \((\d+)d(\d+)(?:\s*([+\-−])\s*(\d+))?\) ([A-Za-z]+) damage at the start of each of its turns\.??",
    re.I,
)
_ATTACHED_DRAIN = re.compile(
    r"(?:and\s+)?the (?P<source>[^.]+?) attaches to the target\.\s*"
    r"While attached, the (?P=source) doesn['’]t attack\.\s*Instead, at the start of each of the (?P=source)['’]s turns, the target loses \d+ \((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+\-−])\s*(?P<bonus>\d+))?\) hit points due to blood loss\.\s*"
    r"The (?P=source) can detach itself by spending (?P<movement>\d+) feet of its movement\.\s*"
    r"It does so after it drains (?P<threshold>\d+) hit points of blood from the target or the target dies\.\s*"
    r"A creature, including the target, can use its action to detach the (?P=source)\.??",
    re.I,
)
_IGNITION_START = re.compile(
    r"If the target is a creature or a flammable object, it ignites\.\s*"
    r"Until a creature takes an action to douse the fire, the target takes \d+ \((\d+)d(\d+)(?:\s*([+\-−])\s*(\d+))?\) fire damage at the start of each of its turns\.??",
    re.I,
)
_DAMAGE_TYPES = {"acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic", "piercing", "poison", "psychic", "radiant", "slashing", "thunder"}


def _modifier(sign: str | None, bonus: str | None) -> int:
    return int(bonus or 0) * (-1 if sign in {"-", "−"} else 1)


def parse_ongoing_damage(text: str, attack: dict) -> tuple[dict | None, dict | None, str]:
    infernal = _INFERNAL_WOUND.search(text)
    if infernal:
        dc, count, size, increment_count, increment_size, removal_dc = map(int, infernal.groups())
        if (count, size) != (increment_count, increment_size): return None, None, text
        save = {
            "save_ability": "constitution", "dc": dc, "excluded_creature_types": ["undead", "construct"],
            "gates_ongoing_damage": True,
        }
        ongoing = {
            "id": "infernal-wound", "name": "Infernal Wound", "dice_count": count, "dice_size": size,
            "apply_on": "failed_on_hit_save", "stacks_on_reapply": True, "ends_on_magical_healing": True,
            "removal_ability": "wisdom", "removal_skill": "medicine", "removal_dc": removal_dc,
        }
        residual = f"{text[:infernal.start()]} {text[infernal.end():]}".strip(" .,;")
        return ongoing, save, residual
    ignition = _IGNITION_START.search(text)
    if ignition:
        count, size, sign, bonus = ignition.groups()
        ongoing = {
            "id": "ignited", "name": "Burning", "dice_count": int(count), "dice_size": int(size),
            "damage_bonus": _modifier(sign, bonus), "damage_type": "fire", "apply_on": "hit",
            "tick_timing": "target_turn_start", "action_removable": True, "action_removal_range_ft": 5,
        }
        residual = f"{text[:ignition.start()]} {text[ignition.end():]}".strip(" .,;")
        return ongoing, None, residual
    attached = _ATTACHED_DRAIN.search(text)
    if attached:
        data = attached.groupdict()
        ongoing = {
            "id": "attached-blood-drain", "name": attack.get("name", "Blood Drain"),
            "dice_count": int(data["count"]), "dice_size": int(data["size"]),
            "damage_bonus": _modifier(data["sign"], data["bonus"]), "tick_timing": "source_turn_start",
            "blocks_source_attacks": True, "action_removable": True, "action_removal_range_ft": 5,
            "source_detach_movement_ft": int(data["movement"]), "auto_end_after_hp_loss": int(data["threshold"]),
        }
        residual = f"{text[:attached.start()]} {text[attached.end():]}".strip(" .,;")
        return ongoing, None, residual
    control = attack.get("control_effect") or {}
    grapple = _GRAPPLE_DAMAGE.search(text)
    if grapple and control.get("grapple_escape_dc"):
        count, size, sign, bonus, damage_type = grapple.groups(); damage_type = damage_type.lower()
        if damage_type not in _DAMAGE_TYPES: return None, None, text
        ongoing = {
            "id": "grapple-start-turn-damage", "name": f"{attack.get('name', 'Grapple')} grapple",
            "dice_count": int(count), "dice_size": int(size), "damage_bonus": _modifier(sign, bonus), "damage_type": damage_type,
            "apply_on": "hit", "ends_when_grapple_source_ends": True,
        }
        residual = f"{text[:grapple.start()]} {text[grapple.end():]}".strip(" .,;")
        return ongoing, None, residual
    return None, None, text


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich 2014 attack-applied ongoing damage effects.")
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8")); parsed = 0
        for monster in catalog:
            for attack in monster.get("attacks", []):
                if attack.get("source_complete", True): continue
                ongoing, save, residual = parse_ongoing_damage(attack.get("unsupported_text") or "", attack)
                if ongoing is None: continue
                attack["ongoing_damage_effect"] = ongoing
                if save is not None: attack["on_hit_save_effect"] = save
                attack["unsupported_text"] = residual or None; attack["source_complete"] = not residual; parsed += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed} ongoing attack damage rider(s)")
        return 0
    except Exception as exc:
        logger.exception("2014 ongoing damage enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
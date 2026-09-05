from __future__ import annotations

from app.content.monster_simple_actions import (
    parse_single_attack,
    parse_single_recharge_save,
    parse_uniform_multiattack_count,
)
from app.content.monster_source_definition import source_definition_fields, source_row, slug
from app.domain.capabilities import CombatantDefinition

RECHARGE_MONSTER_NAMES = (
    "Hell Hound",
    "Black Dragon Wyrmling", "Young Black Dragon",
    "Blue Dragon Wyrmling", "Young Blue Dragon",
    "Green Dragon Wyrmling", "Young Green Dragon",
    "Red Dragon Wyrmling", "Young Red Dragon",
    "White Dragon Wyrmling", "Young White Dragon",
)


def _body_style(name: str, creature_type: object) -> str:
    if "dragon" in str(creature_type).lower():
        return "dragon"
    if "hound" in name.lower():
        return "quadruped"
    return "monster"


def _definition(name: str) -> CombatantDefinition:
    row = source_row(name)
    payload = source_definition_fields(name)
    attack = parse_single_attack(row)
    save_action, resource = parse_single_recharge_save(row)
    count = parse_uniform_multiattack_count(row, str(attack["name"]))
    monster_id = f"srd-{slug(name)}"
    payload.update({
        "archetype": "source-certified recharge monster",
        "attacks": [attack], "primary_attack_id": attack["id"],
        "attack_action": {
            "id": f"{monster_id}-multiattack", "name": "Multiattack",
            "slots": [{"attack_ids": [attack["id"]]} for _ in range(count)],
        },
        "save_actions": [save_action], "resources": [resource],
        "visual": {"armor": "natural", "main_hand": str(attack["name"]).lower(),
                   "body_style": _body_style(name, row.get("type"))},
    })
    return CombatantDefinition.model_validate(payload)


def build_recharge_monster_definitions() -> dict[str, CombatantDefinition]:
    definitions = [_definition(name) for name in RECHARGE_MONSTER_NAMES]
    return {item.id: item for item in definitions}

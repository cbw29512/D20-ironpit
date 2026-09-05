from __future__ import annotations

from app.content.monster_simple_actions import parse_attack_rolls, parse_uniform_multiattack_count
from app.content.monster_source_definition import slug, source_definition_fields, source_row
from app.domain.capabilities import CombatantDefinition

_RECHARGE_ATTACK_MONSTERS = ("Ape",)


def build_recharge_attack_monster_definitions() -> dict[str, CombatantDefinition]:
    """Compile strict source-driven monsters with one normal Multiattack and one recharge attack roll."""
    definitions: dict[str, CombatantDefinition] = {}
    for name in _RECHARGE_ATTACK_MONSTERS:
        row = source_row(name); attacks, resources = parse_attack_rolls(row)
        unlimited = [attack for attack in attacks if not attack.get("resource_id")]
        limited = [attack for attack in attacks if attack.get("resource_id")]
        if len(unlimited) != 1 or len(limited) != 1 or len(resources) != 1:
            raise ValueError(f"Recharge attack family shape changed for {name!r}.")
        primary = unlimited[0]; count = parse_uniform_multiattack_count(row, str(primary["name"]))
        monster_id = f"srd-{slug(name)}"; payload = source_definition_fields(name)
        payload.update({
            "archetype": "source-derived recharge attacker", "attacks": attacks,
            "primary_attack_id": primary["id"], "resources": resources,
            "attack_action": {"id": f"{monster_id}-multiattack", "name": "Multiattack",
                              "slots": [{"attack_ids": [primary["id"]]} for _ in range(count)]},
            "visual": {"armor": "natural", "main_hand": str(primary["name"]).lower(), "body_style": "monster"},
        })
        definition = CombatantDefinition.model_validate(payload)
        definitions[definition.id] = definition
    return definitions

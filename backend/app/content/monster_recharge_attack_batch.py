from __future__ import annotations

from app.content.monster_catalog import load_monster_rows
from app.content.monster_simple_actions import parse_attack_rolls, parse_uniform_multiattack_count
from app.content.monster_source_definition import slug, source_definition_fields
from app.domain.capabilities import CombatantDefinition


def _family_parts(row: dict[str, object]):
    attacks, resources = parse_attack_rolls(row)
    unlimited = [attack for attack in attacks if not attack.get("resource_id")]
    limited = [attack for attack in attacks if attack.get("resource_id")]
    if len(unlimited) != 1 or len(limited) != 1 or len(resources) != 1:
        return None
    try:
        count = parse_uniform_multiattack_count(row, str(unlimited[0]["name"]))
    except ValueError:
        return None
    return attacks, resources, unlimited[0], count


def discover_recharge_attack_names() -> tuple[str, ...]:
    """Discover strict SRD rows whose combat shape is one normal Multiattack plus one recharge attack roll."""
    return tuple(
        str(row["name"])
        for row in load_monster_rows()
        if _family_parts(row) is not None
    )


def build_recharge_attack_monster_definitions() -> dict[str, CombatantDefinition]:
    """Compile every strict source-derived recharge-attack family member; full source audit decides readiness."""
    definitions: dict[str, CombatantDefinition] = {}
    rows = {str(row["name"]): row for row in load_monster_rows()}
    for name in discover_recharge_attack_names():
        row = rows[name]; parts = _family_parts(row)
        if parts is None:
            raise RuntimeError(f"Discovered recharge attack family member {name!r} no longer matches its source shape.")
        attacks, resources, primary, count = parts
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

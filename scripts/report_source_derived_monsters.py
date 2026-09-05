from __future__ import annotations

from collections import defaultdict

from app.content.capability_compiler import compile_combatant
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_creature_types import complete_monster_creature_types
from app.content.monster_simple_actions import parse_single_attack, parse_single_recharge_save, parse_uniform_multiattack_count
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_source_definition import slug, source_definition_fields
from app.domain.capabilities import CombatantDefinition
from app.domain.catalog import CoverageStatus


def _simple_definition(row: dict[str, object], *, recharge: bool) -> CombatantDefinition:
    name = str(row["name"]); monster_id = f"srd-{slug(name)}"
    payload = source_definition_fields(name)
    attack = parse_single_attack(row)
    payload.update({
        "archetype": "source-derived simple monster", "attacks": [attack], "primary_attack_id": attack["id"],
        "visual": {"armor": "natural", "main_hand": str(attack["name"]).lower(), "body_style": "monster"},
    })
    actions = str(row.get("actions", ""))
    if "Multiattack." in actions:
        count = parse_uniform_multiattack_count(row, str(attack["name"]))
        payload["attack_action"] = {
            "id": f"{monster_id}-multiattack", "name": "Multiattack",
            "slots": [{"attack_ids": [attack["id"]]} for _ in range(count)],
        }
    if recharge:
        save_action, resource = parse_single_recharge_save(row)
        payload["save_actions"] = [save_action]
        payload["resources"] = [resource]
    return CombatantDefinition.model_validate(payload)


def _passes(row: dict[str, object], recharge: bool) -> bool:
    try:
        definition = _simple_definition(row, recharge=recharge)
        template = complete_monster_creature_types([compile_combatant(definition)])[0]
        return audit_monster_source(template, row) == []
    except (ValueError, RuntimeError):
        return False


def main() -> None:
    ready = {card.name for card in build_monster_catalog() if card.coverage_status is CoverageStatus.RAW_READY}
    families: dict[str, list[str]] = defaultdict(list)
    for row in load_monster_rows():
        name = str(row["name"])
        if name in ready:
            continue
        if _passes(row, recharge=True):
            families["single-attack+recharge-area-save"].append(name)
        elif _passes(row, recharge=False):
            families["single-attack"].append(name)
    total = sum(len(names) for names in families.values())
    print(f"SOURCE_DERIVED_CANDIDATES total={total}")
    for family, names in sorted(families.items()):
        print(f"SOURCE_DERIVED_FAMILY family={family} count={len(names)} names={';'.join(sorted(names))}")


if __name__ == "__main__":
    main()

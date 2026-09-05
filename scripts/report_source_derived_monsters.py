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
from report_zero_engine_monsters import _source_blockers


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


def _parser_family(row: dict[str, object]) -> str | None:
    for family, recharge in (("single-attack+recharge-area-save", True), ("single-attack", False)):
        try:
            definition = _simple_definition(row, recharge=recharge)
            template = complete_monster_creature_types([compile_combatant(definition)])[0]
            if audit_monster_source(template, row) == []:
                return family
        except (ValueError, RuntimeError):
            continue
    return None


def main() -> None:
    rows = load_monster_rows(); monster_names = {str(row["name"]) for row in rows}
    cards = build_monster_catalog()
    ready = {card.name for card in cards if card.coverage_status is CoverageStatus.RAW_READY}
    deferred = {
        card.name for card in cards
        if any(blocker.startswith("deferred-environment:") for blocker in card.blockers)
    }
    safe: dict[str, list[str]] = defaultdict(list)
    semantic_blocked: dict[str, list[str]] = defaultdict(list)
    parser_clean_deferred: list[str] = []
    for row in rows:
        name = str(row["name"])
        if name in ready:
            continue
        family = _parser_family(row)
        if family is None:
            continue
        if name in deferred:
            parser_clean_deferred.append(name)
            continue
        blockers = _source_blockers(row, monster_names)
        if blockers:
            semantic_blocked["+".join(sorted(set(blockers)))].append(name)
            continue
        safe[family].append(name)
    total = sum(len(names) for names in safe.values())
    blocked_total = sum(len(names) for names in semantic_blocked.values())
    print(f"SOURCE_DERIVED_CANDIDATES total={total}")
    for family, names in sorted(safe.items()):
        print(f"SOURCE_DERIVED_FAMILY family={family} count={len(names)} names={';'.join(sorted(names))}")
    print(f"SOURCE_DERIVED_PARSER_CLEAN_BLOCKED total={blocked_total}")
    for signature, names in sorted(semantic_blocked.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"SOURCE_DERIVED_BLOCKED blockers={signature} count={len(names)} names={';'.join(sorted(names))}")
    print(
        "SOURCE_DERIVED_PARSER_CLEAN_DEFERRED "
        f"total={len(parser_clean_deferred)} names={';'.join(sorted(parser_clean_deferred))}"
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.monster_saving_throws import parse_saving_throw_bonuses
from app.content.monster_trait_source_audit import _MODELED_TRAITS, parse_trait_names
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.content.simple_monster_source_attacks import parse_simple_attacks
from app.domain.capabilities import CombatantDefinition

_SIMPLE_SOURCE_NAMES = frozenset({"Blink Dog", "Fire Giant", "Nightmare", "Sahuagin Warrior", "Spy", "Tough Boss", "Xorn"})


def _first_int(value: object) -> int:
    match = re.search(r"-?\d+", str(value))
    if match is None:
        raise ValueError(f"No integer in SRD value {value!r}.")
    return int(match.group())


def _initiative(row: dict[str, object]) -> int:
    match = re.search(r"\bInitiative\s+([+-]?\d+)", str(row.get("rawText", "")), re.I)
    if match is None:
        raise ValueError(f"Missing initiative for {row.get('name')!r}.")
    return int(match.group(1))


def _definition(row: dict[str, object]) -> CombatantDefinition:
    attacks, multiattack = parse_simple_attacks(row)
    defenses = parse_defense_profile(row)
    trait_names = parse_trait_names(row.get("traits", "")) if str(row.get("traits", "")).strip() else []
    combat_traits = [_MODELED_TRAITS[name].value for name in trait_names if name in _MODELED_TRAITS]
    name = str(row["name"])
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    data: dict[str, object] = {
        "schema_version": 1,
        "id": f"srd-{slug}",
        "name": name,
        "archetype": "source-certified monster",
        "challenge_rating": str(row["challenge"]).split()[0],
        "kind": "monster",
        "size": str(row["size"]).split()[0].lower(),
        "armor_class": _first_int(row["armorClass"]),
        "max_hp": _first_int(row["hitPoints"]),
        "speed_ft": standard_arena_closing_speed(row["speed"]),
        "movement_modes": parse_movement_profile(row["speed"]).model_dump(mode="json"),
        "initiative_bonus": _initiative(row),
        "attacks": attacks,
        "primary_attack_id": attacks[0]["id"],
        "saving_throw_bonuses": parse_saving_throw_bonuses(row),
        "combat_traits": combat_traits,
        "source_trait_names": trait_names,
        "damage_vulnerabilities": sorted(defenses["damage_vulnerabilities"]),
        "damage_resistances": sorted(defenses["damage_resistances"]),
        "damage_immunities": sorted(defenses["damage_immunities"]),
        "condition_immunities": sorted(defenses["condition_immunities"]),
        "visual": {"armor": "natural", "main_hand": attacks[0]["name"], "body_style": "monster"},
        "source": str(row["sourceReference"]),
    }
    if multiattack is not None:
        data["attack_action"] = multiattack
    return CombatantDefinition.model_validate(data)


def build_simple_source_definitions() -> dict[str, CombatantDefinition]:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    missing = _SIMPLE_SOURCE_NAMES - rows.keys()
    if missing:
        raise ValueError(f"Missing SRD simple-monster rows: {', '.join(sorted(missing))}")
    definitions = [_definition(rows[name]) for name in sorted(_SIMPLE_SOURCE_NAMES)]
    result = {definition.id: definition for definition in definitions}
    if len(result) != len(definitions):
        raise ValueError("Simple source-derived monster ids must be unique.")
    return result

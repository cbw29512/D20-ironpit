from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.monster_limited_use_source_audit import parse_action_recharges, parse_limited_use_names
from app.content.monster_saving_throws import parse_saving_throw_bonuses
from app.content.monster_simple_attack_parser import first_attack_start, parse_simple_attacks
from app.content.monster_simple_save_control_parser import parse_simple_save_control_actions
from app.content.monster_simple_save_parser import parse_simple_save_actions
from app.content.monster_source_classifier import source_blockers
from app.content.monster_trait_source_audit import _MODELED_TRAITS, parse_trait_names
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import CombatantTemplate, DamageType, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.size import CreatureSize

_MULTI_PART = re.compile(r"(?P<count>one|two|three|four|five|six|\d+)\s+(?P<name>[A-Z][A-Za-z0-9 ’'/-]+?)\s+attacks?\b")
_NUMBER = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _number(value: str) -> int:
    return _NUMBER.get(value.lower(), int(value) if value.isdigit() else 0)


def _multiattack(row: dict[str, object], attacks: list[WeaponAttack]) -> AttackActionDefinition | None:
    actions = str(row["actions"])
    if not actions.lower().startswith("multiattack."):
        return None
    intro = actions[:first_attack_start(actions)]
    by_name: dict[str, list[str]] = {}
    for attack in attacks:
        by_name.setdefault(attack.weapon.name, []).append(attack.id)
    combination = re.search(r"makes\s+(one|two|three|four|five|six|\d+)\s+attacks?,\s+using\s+(.+?)\s+in any combination", intro, re.I)
    if combination:
        names = [name.strip() for name in re.split(r"\s+or\s+|,", combination.group(2)) if name.strip()]
        ids = [attack_id for name in names for attack_id in by_name.get(name, [])]
        if not ids:
            raise ValueError("multiattack combination names do not match parsed attacks")
        return AttackActionDefinition(
            id=f"srd-{_slug(str(row['name']))}-multiattack",
            name="Multiattack",
            slots=[AttackActionSlot(attack_ids=ids) for _ in range(_number(combination.group(1)))],
        )
    parts = list(_MULTI_PART.finditer(intro))
    if not parts:
        raise ValueError("simple multiattack sequence could not be parsed")
    slots: list[AttackActionSlot] = []
    for part in parts:
        ids = by_name.get(part.group("name"), [])
        if not ids:
            raise ValueError("multiattack attack name does not match parsed attacks")
        slots.extend(AttackActionSlot(attack_ids=ids) for _ in range(_number(part.group("count"))))
    return AttackActionDefinition(id=f"srd-{_slug(str(row['name']))}-multiattack", name="Multiattack", slots=slots)


def _recharge_resources(row: dict[str, object]) -> list[ResourceDefinition]:
    monster_slug = _slug(str(row["name"]))
    return [
        ResourceDefinition(
            id=f"srd-{monster_slug}-{_slug(name)}-recharge",
            name=name,
            max_uses=1,
            recharge_d6_min=minimum,
        )
        for name, minimum in parse_action_recharges(row).items()
    ]


def compile_simple_monster(row: dict[str, object], monster_names: set[str]) -> CombatantTemplate:
    try:
        if source_blockers(row, monster_names):
            raise ValueError("source requires mechanics outside the simple universal compiler")
        if str(row.get("reactions", "")).strip() or "Spellcasting." in str(row.get("actions", "")):
            raise ValueError("source needs a modeled reaction or spellcasting fingerprint")
        attacks = parse_simple_attacks(row)
        save_actions = [*parse_simple_save_actions(row), *parse_simple_save_control_actions(row)]
        defenses = parse_defense_profile(row)
        raw = str(row["rawText"])
        initiative = re.search(r"\bInitiative\s+([+-]?\d+)", raw, re.I)
        if initiative is None:
            raise ValueError("source initiative missing")
        traits = parse_trait_names(row.get("traits", ""))
        return CombatantTemplate(
            id=f"srd-{_slug(str(row['name']))}", name=str(row["name"]), archetype="source-compiled monster", kind="monster",
            size=CreatureSize(str(row["size"]).split()[0].lower()), armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
            max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()), speed_ft=standard_arena_closing_speed(row["speed"]),
            movement_modes=parse_movement_profile(row["speed"]), initiative_bonus=int(initiative.group(1)),
            challenge_rating=str(row["challenge"]).split()[0], weapon_attack=attacks[0], alternate_weapon_attacks=attacks[1:],
            attack_action=_multiattack(row, attacks), saving_throw_actions=save_actions,
            combat_traits=[_MODELED_TRAITS[name] for name in traits if name in _MODELED_TRAITS],
            source_trait_names=traits, source_limited_use_names=parse_limited_use_names(row), resources=_recharge_resources(row),
            saving_throw_bonuses=parse_saving_throw_bonuses(row),
            damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
            damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
            damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])], condition_immunities=sorted(defenses["condition_immunities"]),
            visual=VisualLoadout(armor="natural", main_hand=attacks[0].weapon.name, body_style="monster"), source=str(row["sourceReference"]),
        )
    except Exception as exc:
        raise ValueError(f"simple monster compilation failed for {row.get('name', '<unknown>')}") from exc


def build_auto_simple_monsters(existing_names: set[str]) -> list[CombatantTemplate]:
    rows = load_monster_rows(); names = {str(row["name"]) for row in rows}; compiled: list[CombatantTemplate] = []
    for row in rows:
        name = str(row["name"])
        if name in existing_names or source_blockers(row, names):
            continue
        try:
            compiled.append(compile_simple_monster(row, names))
        except ValueError as exc:
            raise RuntimeError(f"Source-safe monster {name!r} failed compilation.") from exc
    return compiled

from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.monster_saving_throws import parse_saving_throw_bonuses
from app.content.monster_source_classifier import source_blockers
from app.content.monster_trait_source_audit import _MODELED_TRAITS, parse_trait_names
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import CombatantTemplate, DamageType, OnHitDamage, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize

_ATTACK = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9 ’'()/-]+)\.\s+(?P<mode>Melee|Ranged|Melee or Ranged)\s+Attack Roll:\s*"
    r"(?P<bonus>[+-]?\d+),\s*(?P<range>[^.]+)\.\s+Hit:\s*(?P<hit>.*?)(?=(?:\s+[A-Z][A-Za-z0-9 ’'()/-]+\.\s+"
    r"(?:Melee|Ranged|Melee or Ranged)\s+Attack Roll:)|$)", re.S,
)
_DICE_DAMAGE = re.compile(
    r"\d+\s*\(\s*(?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\s*\)\s+"
    r"(?P<type>Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder)\s+damage",
    re.I,
)
_FIXED_DAMAGE = re.compile(
    r"^(?P<amount>\d+)\s+(?P<type>Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder)\s+damage\b",
    re.I,
)
_REACH = re.compile(r"reach\s+(\d+)\s*ft", re.I)
_RANGE = re.compile(r"range\s+(\d+)\s*/\s*(\d+)\s*ft", re.I)
_MULTI_PART = re.compile(r"(?P<count>one|two|three|four|five|six|\d+)\s+(?P<name>[A-Z][A-Za-z0-9 ’'/-]+?)\s+attacks?\b")
_NUMBER = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _number(value: str) -> int:
    return _NUMBER.get(value.lower(), int(value) if value.isdigit() else 0)


def _damage(hit: str) -> tuple[int, int, int, DamageType, int | None, list[OnHitDamage]]:
    matches = list(_DICE_DAMAGE.finditer(hit))
    if matches:
        first = matches[0]
        bonus = int(first.group("bonus") or 0) * (-1 if first.group("sign") == "-" else 1)
        extras = []
        for item in matches[1:]:
            extra_bonus = int(item.group("bonus") or 0) * (-1 if item.group("sign") == "-" else 1)
            extras.append(OnHitDamage(
                source=item.group("type").title(), dice_count=int(item.group("count")), dice_size=int(item.group("size")),
                damage_bonus=extra_bonus, damage_type=DamageType(item.group("type").lower()),
            ))
        return int(first.group("count")), int(first.group("size")), bonus, DamageType(first.group("type").lower()), None, extras
    fixed = _FIXED_DAMAGE.search(hit.strip())
    if fixed:
        return 0, 2, 0, DamageType(fixed.group("type").lower()), int(fixed.group("amount")), []
    raise ValueError("attack damage is not a simple supported damage clause")


def _attacks(row: dict[str, object]) -> list[WeaponAttack]:
    attacks: list[WeaponAttack] = []
    for match in _ATTACK.finditer(str(row["actions"])):
        count, size, damage_bonus, damage_type, fixed, extras = _damage(match.group("hit"))
        modes = ["melee", "ranged"] if match.group("mode").lower() == "melee or ranged" else [match.group("mode").lower()]
        for mode in modes:
            reach = _REACH.search(match.group("range")); ranged = _RANGE.search(match.group("range"))
            if mode == "melee" and reach is None:
                raise ValueError("simple melee attack lacks reach")
            if mode == "ranged" and ranged is None:
                raise ValueError("simple ranged attack lacks range")
            suffix = f"-{mode}" if len(modes) > 1 else ""
            attack_id = f"srd-{_slug(str(row['name']))}-{_slug(match.group('name'))}{suffix}"
            weapon = Weapon(
                id=f"{attack_id}-weapon", name=match.group("name"), attack_kind=WeaponAttackKind(mode),
                dice_count=count, dice_size=size, damage_type=damage_type, reach_ft=int(reach.group(1)) if reach else 5,
                normal_range_ft=int(ranged.group(1)) if ranged else None, long_range_ft=int(ranged.group(2)) if ranged else None,
                animation="strike",
            )
            attacks.append(WeaponAttack(
                id=attack_id, weapon=weapon, attack_bonus=int(match.group("bonus")), damage_bonus=damage_bonus,
                fixed_damage=fixed, on_hit_damage=extras,
            ))
    if not attacks:
        raise ValueError("no simple attacks parsed")
    return attacks


def _multiattack(row: dict[str, object], attacks: list[WeaponAttack]) -> AttackActionDefinition | None:
    actions = str(row["actions"])
    if not actions.lower().startswith("multiattack."):
        return None
    intro = actions[:_ATTACK.search(actions).start()]
    by_name: dict[str, list[str]] = {}
    for attack in attacks:
        by_name.setdefault(attack.weapon.name, []).append(attack.id)
    combination = re.search(r"makes\s+(one|two|three|four|five|six|\d+)\s+attacks?,\s+using\s+(.+?)\s+in any combination", intro, re.I)
    if combination:
        names = [name.strip() for name in re.split(r"\s+or\s+|,", combination.group(2)) if name.strip()]
        ids = [attack_id for name in names for attack_id in by_name.get(name, [])]
        if not ids:
            raise ValueError("multiattack combination names do not match parsed attacks")
        return AttackActionDefinition(id=f"srd-{_slug(str(row['name']))}-multiattack", name="Multiattack", slots=[AttackActionSlot(attack_ids=ids) for _ in range(_number(combination.group(1)))])
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


def compile_simple_monster(row: dict[str, object], monster_names: set[str]) -> CombatantTemplate:
    if source_blockers(row, monster_names):
        raise ValueError("source requires mechanics outside the simple universal compiler")
    if str(row.get("reactions", "")).strip() or str(row.get("bonusActions", "")).strip() or "Spellcasting." in str(row.get("actions", "")):
        raise ValueError("source needs a modeled reaction, bonus action, or spellcasting fingerprint")
    attacks = _attacks(row)
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
        attack_action=_multiattack(row, attacks), combat_traits=[_MODELED_TRAITS[name] for name in traits if name in _MODELED_TRAITS],
        source_trait_names=traits, saving_throw_bonuses=parse_saving_throw_bonuses(row),
        damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
        damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
        damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
        condition_immunities=sorted(defenses["condition_immunities"]),
        visual=VisualLoadout(armor="natural", main_hand=attacks[0].weapon.name, body_style="monster"), source=str(row["sourceReference"]),
    )


def build_auto_simple_monsters(existing_names: set[str]) -> list[CombatantTemplate]:
    rows = load_monster_rows(); names = {str(row["name"]) for row in rows}; compiled: list[CombatantTemplate] = []
    for row in rows:
        if str(row["name"]) in existing_names:
            continue
        try:
            compiled.append(compile_simple_monster(row, names))
        except ValueError:
            continue
    return compiled

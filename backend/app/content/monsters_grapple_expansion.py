from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.actions import AttackActionDefinition, AttackActionSlot, HitControlEffect
from app.domain.models import CombatantTemplate, DamageType, OnHitDamage, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize

_ATTACKS = {
    "Giant Scorpion": [
        ("Claw", 5, 1, 6, 3, "bludgeoning", CreatureSize.LARGE, 13, []),
        ("Sting", 5, 1, 8, 3, "piercing", None, None, [("Poison", 2, 10, 0, "poison")]),
    ],
    "Grick": [
        ("Beak", 4, 2, 6, 2, "piercing", None, None, []),
        ("Tentacles", 4, 1, 10, 2, "slashing", CreatureSize.MEDIUM, 12, []),
    ],
    "Griffon": [("Rend", 6, 1, 8, 4, "piercing", CreatureSize.MEDIUM, 14, [])],
}
_MULTI = {
    "Giant Scorpion": ("Claw", "Claw", "Sting"),
    "Grick": ("Beak", "Tentacles"),
    "Griffon": ("Rend", "Rend"),
}
_SKILLS = {
    "Giant Scorpion": {"athletics": 3, "acrobatics": 1},
    "Grick": {"athletics": 2, "acrobatics": 2, "stealth": 4},
    "Griffon": {"athletics": 4, "acrobatics": 2, "perception": 5},
}
_VISUALS = {
    "Giant Scorpion": ("claw", "giant-scorpion"),
    "Grick": ("tentacles", "grick"),
    "Griffon": ("claw", "griffon"),
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _row(name: str) -> dict[str, object]:
    matches = [row for row in load_monster_rows() if row["name"] == name]
    if len(matches) != 1:
        raise ValueError(f"Expected one SRD source row for {name!r}; found {len(matches)}.")
    return matches[0]


def _attack(monster: str, spec: tuple) -> WeaponAttack:
    name, bonus, count, size, damage_bonus, damage_type, max_size, escape_dc, extras = spec
    attack_id = f"srd-{_slug(monster)}-{_slug(name)}"
    control = None if escape_dc is None else HitControlEffect(max_target_size=max_size, grapple_escape_dc=escape_dc)
    weapon = Weapon(
        id=f"{attack_id}-weapon", name=name, attack_kind=WeaponAttackKind.MELEE,
        dice_count=count, dice_size=size, damage_type=DamageType(damage_type), animation="strike", reach_ft=5,
    )
    on_hit = [
        OnHitDamage(source=source, dice_count=dice_count, dice_size=dice_size, damage_bonus=extra_bonus, damage_type=DamageType(dtype))
        for source, dice_count, dice_size, extra_bonus, dtype in extras
    ]
    return WeaponAttack(
        id=attack_id, weapon=weapon, attack_bonus=bonus, damage_bonus=damage_bonus,
        on_hit_damage=on_hit, control_effect=control,
    )


def _template(name: str) -> CombatantTemplate:
    row = _row(name)
    attacks = [_attack(name, spec) for spec in _ATTACKS[name]]
    by_name = {attack.weapon.name: attack.id for attack in attacks}
    slots = [AttackActionSlot(attack_ids=[by_name[attack_name]]) for attack_name in _MULTI[name]]
    defenses = parse_defense_profile(row)
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row["rawText"]), re.I)
    if initiative is None:
        raise ValueError(f"Missing SRD initiative for {name!r}.")
    main_hand, body_style = _VISUALS[name]
    return CombatantTemplate(
        id=f"srd-{_slug(name)}", name=name, archetype="source-certified grapple monster", kind="monster",
        size=CreatureSize(str(row["size"]).split()[0].lower()), armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()), speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]), initiative_bonus=int(initiative.group(1)),
        challenge_rating=str(row["challenge"]).split()[0], weapon_attack=attacks[0], alternate_weapon_attacks=attacks[1:],
        attack_action=AttackActionDefinition(id=f"srd-{_slug(name)}-multiattack", name="Multiattack", slots=slots),
        skill_bonuses=_SKILLS[name],
        damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
        damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
        damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
        condition_immunities=sorted(defenses["condition_immunities"]),
        visual=VisualLoadout(armor="natural", main_hand=main_hand, body_style=body_style), source=str(row["sourceReference"]),
    )


def build_grapple_expansion() -> list[CombatantTemplate]:
    return [_template(name) for name in _ATTACKS]

from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import CombatantTemplate, DamageType, OnHitDamage, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.reactions import ParryReaction
from app.domain.size import CreatureSize

_ATTACKS = {
    "Bandit Captain": [
        ("Scimitar", "melee", 5, 1, 6, 3, "slashing", 5, None, None, []),
        ("Pistol", "ranged", 5, 1, 10, 3, "piercing", 5, 30, 90, []),
    ],
    "Knight": [
        ("Greatsword", "melee", 5, 2, 6, 3, "slashing", 5, None, None, [("Radiant", 1, 8, "radiant")]),
        ("Heavy Crossbow", "ranged", 2, 2, 10, 0, "piercing", 5, 100, 400, [("Radiant", 1, 8, "radiant")]),
    ],
    "Noble": [("Rapier", "melee", 3, 1, 8, 1, "piercing", 5, None, None, [])],
    "Warrior Veteran": [
        ("Greatsword", "melee", 5, 2, 6, 3, "slashing", 5, None, None, []),
        ("Heavy Crossbow", "ranged", 3, 2, 10, 1, "piercing", 5, 100, 400, []),
    ],
}
_MULTI = {"Bandit Captain": 2, "Knight": 2, "Warrior Veteran": 2}
_ARMOR = {"Bandit Captain": "studded-leather", "Knight": "plate", "Noble": "breastplate", "Warrior Veteran": "splint"}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _row(name: str) -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == name]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD row for {name!r}; found {len(rows)}.")
    return rows[0]


def _attack(monster: str, spec: tuple) -> WeaponAttack:
    name, kind, bonus, count, size, damage_bonus, damage_type, reach, normal, long, extras = spec
    attack_id = f"srd-{_slug(monster)}-{_slug(name)}"
    weapon = Weapon(
        id=f"{attack_id}-weapon", name=name, attack_kind=WeaponAttackKind(kind), dice_count=count,
        dice_size=size, damage_type=DamageType(damage_type), animation="projectile" if kind == "ranged" else "slash",
        reach_ft=reach, normal_range_ft=normal, long_range_ft=long,
        projectile="bolt" if "Crossbow" in name else "bullet" if name == "Pistol" else None,
    )
    on_hit = [OnHitDamage(source=source, dice_count=dice_count, dice_size=dice_size, damage_type=DamageType(dtype))
              for source, dice_count, dice_size, dtype in extras]
    return WeaponAttack(id=attack_id, weapon=weapon, attack_bonus=bonus, damage_bonus=damage_bonus, on_hit_damage=on_hit)


def _template(name: str) -> CombatantTemplate:
    row = _row(name)
    attacks = [_attack(name, spec) for spec in _ATTACKS[name]]
    defenses = parse_defense_profile(row)
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row["rawText"]), re.I)
    if initiative is None:
        raise ValueError(f"Missing SRD initiative for {name!r}.")
    multi_count = _MULTI.get(name)
    attack_action = None if multi_count is None else AttackActionDefinition(
        id=f"srd-{_slug(name)}-multiattack", name="Multiattack",
        slots=[AttackActionSlot(attack_ids=[attack.id for attack in attacks]) for _ in range(multi_count)],
    )
    return CombatantTemplate(
        id=f"srd-{_slug(name)}", name=name, archetype="source-certified Parry monster", kind="monster",
        size=CreatureSize(str(row["size"]).split()[0].lower()), armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()), speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]), initiative_bonus=int(initiative.group(1)),
        challenge_rating=str(row["challenge"]).split()[0], weapon_attack=attacks[0], alternate_weapon_attacks=attacks[1:],
        attack_action=attack_action, parry_reaction=ParryReaction(ac_bonus=2),
        damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
        damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
        damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
        condition_immunities=sorted(defenses["condition_immunities"]),
        visual=VisualLoadout(armor=_ARMOR[name], main_hand=attacks[0].weapon.name, body_style="humanoid"),
        source=str(row["sourceReference"]),
    )


def build_parry_monsters() -> list[CombatantTemplate]:
    return [_template(name) for name in _ATTACKS]

from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import CombatantTemplate, DamageType, OnHitDamage, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait

# These stat blocks require only mechanics already represented by Iron Pit.
# Every template still has to pass the normal full SRD source audit before RAW READY.
_ATTACKS = {
    "Animated Armor": [("Slam", "melee", 4, 1, 6, 2, "bludgeoning", None, 5, None, None, [])],
    "Animated Flying Sword": [("Slash", "melee", 4, 1, 8, 2, "slashing", None, 5, None, None, [])],
    "Awakened Tree": [("Slam", "melee", 6, 3, 6, 4, "bludgeoning", None, 10, None, None, [])],
    "Cultist": [("Ritual Sickle", "melee", 3, 1, 4, 1, "slashing", None, 5, None, None, [("Necrotic", 0, 2, 1, "necrotic")])],
    "Flying Snake": [("Bite", "melee", 4, 0, 2, 0, "piercing", 1, 5, None, None, [("Poison", 2, 4, 0, "poison")])],
    "Gargoyle": [("Claw", "melee", 4, 2, 4, 2, "slashing", None, 5, None, None, [])],
    "Grimlock": [("Bone Cudgel", "melee", 5, 1, 6, 3, "bludgeoning", None, 5, None, None, [("Psychic", 1, 4, 0, "psychic")])],
    "Guard Captain": [
        ("Javelin", "melee", 6, 3, 6, 4, "piercing", None, 5, None, None, []),
        ("Javelin", "ranged", 6, 3, 6, 4, "piercing", None, 5, 30, 120, []),
        ("Longsword", "melee", 6, 2, 10, 4, "slashing", None, 5, None, None, []),
    ],
    "Hippopotamus": [("Bite", "melee", 7, 2, 10, 5, "piercing", None, 5, None, None, [])],
    "Killer Whale": [("Bite", "melee", 6, 5, 6, 4, "piercing", None, 5, None, None, [])],
    "Lemure": [("Vile Slime", "melee", 2, 1, 4, 0, "poison", None, 5, None, None, [])],
    "Manticore": [
        ("Rend", "melee", 5, 1, 8, 3, "slashing", None, 5, None, None, []),
        ("Tail Spike", "ranged", 5, 1, 8, 3, "piercing", None, 5, 100, 200, []),
    ],
    "Ogre Zombie": [("Slam", "melee", 6, 2, 8, 4, "bludgeoning", None, 5, None, None, [])],
    "Pegasus": [("Hooves", "melee", 6, 1, 6, 4, "bludgeoning", None, 5, None, None, [("Radiant", 2, 4, 0, "radiant")])],
    "Scorpion": [("Sting", "melee", 2, 0, 2, 0, "piercing", 1, 5, None, None, [("Poison", 1, 6, 0, "poison")])],
    "Skeleton": [
        ("Shortsword", "melee", 5, 1, 6, 3, "piercing", None, 5, None, None, []),
        ("Shortbow", "ranged", 5, 1, 6, 3, "piercing", None, 5, 80, 320, []),
    ],
    "Spider": [("Bite", "melee", 4, 0, 2, 0, "piercing", 1, 5, None, None, [("Poison", 1, 4, 0, "poison")])],
    "Tough": [
        ("Mace", "melee", 4, 1, 6, 2, "bludgeoning", None, 5, None, None, []),
        ("Heavy Crossbow", "ranged", 3, 1, 10, 1, "piercing", None, 5, 100, 400, []),
    ],
    "Venomous Snake": [("Bite", "melee", 4, 1, 4, 2, "piercing", None, 5, None, None, [("Poison", 1, 6, 0, "poison")])],
    "Violet Fungus": [("Rotting Touch", "melee", 2, 1, 8, 0, "necrotic", None, 10, None, None, [])],
    "Zombie": [("Slam", "melee", 3, 1, 8, 1, "bludgeoning", None, 5, None, None, [])],
}
_MULTI = {
    "Animated Armor": (2, ("Slam",)), "Gargoyle": (2, ("Claw",)),
    "Guard Captain": (2, ("Javelin", "Longsword")), "Hippopotamus": (2, ("Bite",)),
    "Manticore": (3, ("Rend", "Tail Spike")), "Violet Fungus": (2, ("Rotting Touch",)),
}
_TRAITS = {
    "Ogre Zombie": [CombatTrait.UNDEAD_FORTITUDE],
    "Tough": [CombatTrait.PACK_TACTICS],
    "Zombie": [CombatTrait.UNDEAD_FORTITUDE],
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _row(name: str) -> dict[str, object]:
    matches = [row for row in load_monster_rows() if row["name"] == name]
    if len(matches) != 1:
        raise ValueError(f"Expected one SRD source row for {name!r}; found {len(matches)}.")
    return matches[0]


def _weapon_attack(monster: str, spec: tuple) -> WeaponAttack:
    name, kind, bonus, count, size, damage_bonus, damage_type, fixed, reach, normal, long, extras = spec
    duplicate_name = sum(1 for item in _ATTACKS[monster] if item[0] == name) > 1
    mode_suffix = f"-{kind}" if duplicate_name else ""
    attack_id = f"srd-{_slug(monster)}-{_slug(name)}{mode_suffix}"
    weapon = Weapon(
        id=f"{attack_id}-weapon", name=name, attack_kind=WeaponAttackKind(kind), dice_count=count,
        dice_size=size, damage_type=DamageType(damage_type), animation="strike", reach_ft=reach,
        normal_range_ft=normal, long_range_ft=long,
    )
    on_hit = [
        OnHitDamage(source=source, dice_count=dice_count, dice_size=dice_size, damage_bonus=extra_bonus, damage_type=DamageType(dtype))
        for source, dice_count, dice_size, extra_bonus, dtype in extras
    ]
    return WeaponAttack(
        id=attack_id, weapon=weapon, attack_bonus=bonus, damage_bonus=damage_bonus,
        fixed_damage=fixed, on_hit_damage=on_hit,
    )


def _multiattack(monster: str, attacks: list[WeaponAttack]) -> AttackActionDefinition | None:
    profile = _MULTI.get(monster)
    if profile is None:
        return None
    count, names = profile
    ids = [attack.id for attack in attacks if attack.weapon.name in names]
    return AttackActionDefinition(
        id=f"srd-{_slug(monster)}-multiattack", name="Multiattack",
        slots=[AttackActionSlot(attack_ids=ids) for _ in range(count)],
    )


def _template(name: str) -> CombatantTemplate:
    row = _row(name)
    attacks = [_weapon_attack(name, spec) for spec in _ATTACKS[name]]
    defenses = parse_defense_profile(row)
    raw = str(row["rawText"])
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", raw, re.I)
    if initiative is None:
        raise ValueError(f"Missing SRD initiative for {name!r}.")
    size_name = str(row["size"]).split()[0].lower()
    return CombatantTemplate(
        id=f"srd-{_slug(name)}", name=name, archetype="source-certified monster", kind="monster",
        size=CreatureSize(size_name), armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]), movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)), challenge_rating=str(row["challenge"]).split()[0],
        weapon_attack=attacks[0], alternate_weapon_attacks=attacks[1:], attack_action=_multiattack(name, attacks),
        combat_traits=_TRAITS.get(name, []),
        damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
        damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
        damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
        condition_immunities=sorted(defenses["condition_immunities"]),
        visual=VisualLoadout(armor="natural", main_hand=attacks[0].weapon.name, body_style="monster"),
        source=str(row["sourceReference"]),
    )


def build_zero_engine_monsters() -> list[CombatantTemplate]:
    return [_template(name) for name in _ATTACKS]

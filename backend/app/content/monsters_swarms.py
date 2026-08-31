from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.models import CombatantTemplate, ConditionalDamage, DamageType, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait

_SPECS = {
    "Swarm of Bats": ("Bites", 4, 2, 4, 0, 1, 4, "piercing", None),
    "Swarm of Rats": ("Bites", 2, 2, 4, 0, 1, 4, "piercing", None),
    "Swarm of Crawling Claws": ("Swarm of Grasping Hands", 4, 4, 8, 2, 2, 8, "necrotic", CreatureSize.MEDIUM),
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _row(name: str) -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == name]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD row for {name!r}; found {len(rows)}.")
    return rows[0]


def _template(name: str) -> CombatantTemplate:
    row = _row(name)
    action, bonus, base_count, base_size, base_bonus, blood_count, blood_size, damage_type, prone_size = _SPECS[name]
    attack_id = f"srd-{_slug(name)}-{_slug(action)}"
    attack = WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=f"{attack_id}-weapon", name=action, attack_kind=WeaponAttackKind.MELEE,
            dice_count=base_count, dice_size=base_size, damage_type=DamageType(damage_type),
            animation="swarm", reach_ft=5,
        ),
        attack_bonus=bonus, damage_bonus=base_bonus, knocks_prone_max_size=prone_size,
        conditional_damage=[ConditionalDamage(
            trigger="attacker_bloodied", mode="replace_weapon",
            dice_count=blood_count, dice_size=blood_size, damage_bonus=base_bonus,
            damage_type=DamageType(damage_type),
        )],
    )
    defenses = parse_defense_profile(row)
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row["rawText"]), re.I)
    if initiative is None:
        raise ValueError(f"Missing SRD initiative for {name!r}.")
    return CombatantTemplate(
        id=f"srd-{_slug(name)}", name=name, archetype="source-certified swarm candidate", kind="monster",
        size=CreatureSize(str(row["size"]).split()[0].lower()),
        armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]), movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)), challenge_rating=str(row["challenge"]).split()[0],
        weapon_attack=attack, combat_traits=[CombatTrait.SWARM],
        damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
        damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
        damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
        condition_immunities=sorted(defenses["condition_immunities"]),
        visual=VisualLoadout(armor="none", main_hand=action, body_style="swarm"),
        source=str(row["sourceReference"]),
    )


def build_swarm_candidates() -> list[CombatantTemplate]:
    return [_template(name) for name in _SPECS]

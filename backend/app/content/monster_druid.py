from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.content.offensive_spell_effects import build_guiding_bolt, build_inflict_wounds
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.combatants import ResourceDefinition
from app.domain.models import (
    CombatantTemplate,
    DamageType,
    OnHitDamage,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.size import CreatureSize
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.spells import DefensiveSpellAction


def _row() -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == "Druid"]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD source row for Druid; found {len(rows)}.")
    return rows[0]


def _vine_staff() -> WeaponAttack:
    return WeaponAttack(
        id="srd-druid-vine-staff",
        weapon=Weapon(
            id="srd-druid-vine-staff-weapon",
            name="Vine Staff",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=8,
            damage_type=DamageType.BLUDGEONING,
            animation="staff",
            reach_ft=5,
        ),
        attack_bonus=5,
        damage_bonus=3,
        on_hit_damage=[
            OnHitDamage(
                source="Poison",
                dice_count=1,
                dice_size=4,
                damage_bonus=0,
                damage_type=DamageType.POISON,
            )
        ],
    )


def _verdant_wisp() -> WeaponAttack:
    return WeaponAttack(
        id="srd-druid-verdant-wisp",
        weapon=Weapon(
            id="srd-druid-verdant-wisp-weapon",
            name="Verdant Wisp",
            attack_kind=WeaponAttackKind.RANGED,
            dice_count=3,
            dice_size=6,
            damage_type=DamageType.RADIANT,
            animation="spell-projectile",
            reach_ft=5,
            normal_range_ft=90,
            long_range_ft=90,
        ),
        attack_bonus=5,
        damage_bonus=0,
    )


def _longstrider() -> DefensiveSpellAction:
    return DefensiveSpellAction(
        id="longstrider",
        name="Longstrider",
        level=1,
        action_cost="action",
        range_ft=0,
        duration_minutes=60,
        target_policy="self",
        modifier_effects=[SpellModifierEffect(kind="speed", flat_bonus=10)],
        priority=20,
        animation="longstrider",
        source="Iron Pit arena modeling of SRD Longstrider",
    )


def _moonbeam_substitution():
    """Use the certified Inflict Wounds primitive at level 2 as the arena replacement."""
    return build_inflict_wounds(save_dc=13).model_copy(update={
        "level": 2,
        "damage_dice_count": 3,
    })


def build_druid_monster() -> CombatantTemplate:
    row = _row()
    defenses = parse_defense_profile(row)
    raw = str(row["rawText"])
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", raw, re.IGNORECASE)
    if initiative is None:
        raise ValueError("Druid source is missing Initiative.")

    staff = _vine_staff()
    wisp = _verdant_wisp()
    return CombatantTemplate(
        id="srd-druid",
        name="Druid",
        archetype="source-certified monster",
        challenge_rating=str(row["challenge"]).split()[0],
        kind="monster",
        creature_type="Humanoid (Druid)",
        size=CreatureSize.MEDIUM,
        armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)),
        weapon_attack=staff,
        alternate_weapon_attacks=[wisp],
        attack_action=AttackActionDefinition(
            id="srd-druid-multiattack",
            name="Multiattack",
            slots=[
                AttackActionSlot(attack_ids=[staff.id, wisp.id]),
                AttackActionSlot(attack_ids=[staff.id, wisp.id]),
            ],
        ),
        spell_attack_actions=[build_guiding_bolt(attack_bonus=5)],
        spell_save_actions=[_moonbeam_substitution()],
        defensive_spell_actions=[_longstrider()],
        damage_vulnerabilities=[
            DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])
        ],
        damage_resistances=[
            DamageType(item) for item in sorted(defenses["damage_resistances"])
        ],
        damage_immunities=[
            DamageType(item) for item in sorted(defenses["damage_immunities"])
        ],
        condition_immunities=sorted(defenses["condition_immunities"]),
        resources=[
            ResourceDefinition(id="spell-slot-1", name="Level 1 Arena Spell Uses", max_uses=5),
            ResourceDefinition(id="spell-slot-2", name="Level 2 Arena Spell Uses", max_uses=1),
        ],
        visual=VisualLoadout(
            armor="studded-leather",
            main_hand="Vine Staff",
            body_style="humanoid",
        ),
        source=str(row["sourceReference"]),
    )

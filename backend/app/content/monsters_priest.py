from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.domain.models import (
    CombatantTemplate, DamageType, HealingAction, OnHitDamage, ResourceDefinition,
    SupportAction, Weapon, WeaponAttack, WeaponAttackKind,
)


def build_priest_acolyte() -> CombatantTemplate:
    mace = WeaponAttack(
        id="priest-acolyte-mace",
        weapon=Weapon(
            id="priest-acolyte-mace", name="Mace", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=6, damage_type=DamageType.BLUDGEONING, animation="bludgeon",
        ),
        attack_bonus=4, damage_bonus=2,
        on_hit_damage=[OnHitDamage(source="Radiant", dice_count=1, dice_size=4, damage_type=DamageType.RADIANT)],
    )
    flame = WeaponAttack(
        id="priest-acolyte-radiant-flame",
        weapon=Weapon(
            id="priest-acolyte-radiant-flame", name="Radiant Flame", attack_kind=WeaponAttackKind.RANGED,
            dice_count=2, dice_size=6, damage_type=DamageType.RADIANT, animation="projectile",
            normal_range_ft=60, long_range_ft=60, projectile="radiant-flame",
        ),
        attack_bonus=4, damage_bonus=0,
    )
    healing_word = HealingAction(
        id="priest-acolyte-healing-word", name="Healing Word", action_cost="bonus_action",
        range_ft=60, target_mode="self_or_ally", dice_count=2, dice_size=4, healing_bonus=2,
        resource_id="divine-aid", is_spell=True, animation="healing",
    )
    bless = SupportAction(
        id="priest-acolyte-bless", name="Bless", action_cost="bonus_action", effect_id="bless",
        range_ft=30, max_targets=3, duration_rounds=10, concentration=True,
        resource_id="divine-aid", animation="bless",
    )
    sanctuary = SupportAction(
        id="priest-acolyte-sanctuary", name="Sanctuary", action_cost="bonus_action", effect_id="sanctuary",
        range_ft=30, max_targets=1, duration_rounds=10, save_dc=12,
        resource_id="divine-aid", animation="ward",
    )
    return CombatantTemplate(
        id="srd-priest-acolyte", name="Priest Acolyte", archetype="Priest Acolyte",
        challenge_rating="1/4", kind="monster", armor_class=13, max_hp=11, speed_ft=30,
        initiative_bonus=0, weapon_attack=mace, alternate_weapon_attacks=[flame],
        healing_actions=[healing_word], support_actions=[bless, sanctuary],
        saving_throw_bonuses={
            "strength": 2, "dexterity": 0, "constitution": 1,
            "intelligence": 0, "wisdom": 2, "charisma": 0,
        },
        skill_bonuses={"medicine": 4, "religion": 2},
        resources=[ResourceDefinition(id="divine-aid", name="Divine Aid", max_uses=1)],
        visual=build_monster_visual("chain-shirt", "mace", "humanoid"),
        source="SRD 5.2.1 Priest Acolyte p. 316",
    )

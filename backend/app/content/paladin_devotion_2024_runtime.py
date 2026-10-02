from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.character_math import saving_throw_bonuses
from app.content.equipment import build_longsword
from app.content.healing_spell_effects import build_cure_wounds
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.weapon_catalog import build_weapon
from app.domain.actions import ConditionRemovalAction, HealingAction
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _attack(weapon_id: str, strength_modifier: int) -> WeaponAttack:
    weapon = build_longsword() if weapon_id == "longsword" else build_weapon(weapon_id)
    return WeaponAttack(
        id=f"aurelia-{weapon_id}",
        weapon=weapon,
        attack_bonus=2 + strength_modifier,
        damage_bonus=strength_modifier,
        attack_ability="strength",
        attack_ability_modifier=strength_modifier,
    )


def _divine_favor_2024() -> DefensiveSpellAction:
    return DefensiveSpellAction(
        id="divine-favor",
        name="Divine Favor",
        level=1,
        action_cost="bonus_action",
        range_ft=0,
        duration_minutes=1,
        target_policy="self",
        concentration=False,
        priority=40,
        modifier_effects=[SpellModifierEffect(kind="bonus-damage", dice_count=1, dice_size=4, damage_type="radiant")],
        animation="divine-favor",
        source="D&D Beyond Basic Rules 2024: Divine Favor",
    )


def build_aurelia_brightshield_2024(level: int = 1) -> CombatantTemplate:
    """Build the certified 2024 Devotion Paladin using universal combat primitives."""
    try:
        if level != 1:
            raise ValueError("The current 2024 Paladin runtime tranche supports level 1 only.")
        profile = build_aurelia_brightshield_2024_profile(level)
        scores = profile.final_ability_scores
        if scores is None:
            raise ValueError("2024 Aurelia profile is missing final ability scores.")
        strength = scores.modifier("strength")
        charisma = scores.modifier("charisma")
        pb = 2
        return CombatantTemplate(
            id=canonical_template_id("paladin", level),
            name=HERO_BY_CLASS["paladin"].hero_name,
            archetype="Paladin",
            level=level,
            kind="character",
            ruleset="2024",
            creature_type="humanoid",
            ability_scores=scores,
            armor_class=18,
            max_hp=10 + scores.modifier("constitution"),
            speed_ft=30,
            initiative_bonus=scores.modifier("dexterity"),
            starts_with_heroic_inspiration=True,
            weapon_attack=_attack("longsword", strength),
            alternate_weapon_attacks=[_attack("javelin", strength)],
            healing_actions=[
                HealingAction(
                    id="lay-on-hands-heal", name="Lay On Hands", action_cost="bonus_action",
                    range_ft=5, target_mode="self_or_ally", dice_count=0, healing_bonus=5,
                    resource_id="lay-on-hands", resource_cost=5, animation="healing",
                ),
                build_cure_wounds(charisma),
            ],
            condition_removal_actions=[ConditionRemovalAction(
                id="lay-on-hands-poison", name="Lay On Hands", action_cost="bonus_action",
                range_ft=5, target_mode="self_or_ally", removable_conditions=["poisoned"],
                max_conditions_per_use=1, resource_costs_per_condition={"lay-on-hands": 5},
            )],
            defensive_spell_actions=[_divine_favor_2024()],
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("wisdom", "charisma")),
            skill_bonuses={
                "athletics": strength + pb,
                "intimidation": charisma + pb,
                "insight": scores.modifier("wisdom") + pb,
                "persuasion": charisma + pb,
                "perception": scores.modifier("wisdom") + pb,
                "acrobatics": scores.modifier("dexterity") + pb,
                "medicine": scores.modifier("wisdom") + pb,
                "religion": scores.modifier("intelligence") + pb,
            },
            combat_traits=[CombatTrait.SAVAGE_ATTACKER],
            weapon_masteries=["longsword", "javelin"],
            wearing_heavy_armor=True,
            wearing_metal_armor=True,
            visual=VisualLoadout(armor="chain-mail", main_hand="longsword", off_hand="shield"),
            resources=[
                ResourceDefinition(id="lay-on-hands", name="Lay On Hands", max_uses=5),
                ResourceDefinition(id="spell-slot-1", name="Level 1 Spell Slot", max_uses=2),
            ],
            source="D&D Beyond Basic Rules 2024: Paladin 1, Human, Soldier, Cure Wounds, Divine Favor, Longsword, Javelin",
        )
    except Exception:
        logger.exception("Failed to build 2024 Aurelia Brightshield at level %s.", level)
        raise

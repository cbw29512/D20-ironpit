from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.character_math import fixed_hit_points, saving_throw_bonuses
from app.content.equipment import build_longsword
from app.content.healing_spell_effects import build_cure_wounds
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.spell_effects import BLESS
from app.content.weapon_catalog import build_weapon
from app.domain.actions import ConditionRemovalAction, HealingAction
from app.domain.attack_action_weapon_buffs import AttackActionWeaponBuff
from app.domain.models import CombatantTemplate, DamageType, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.post_hit_damage import ResourceBackedPostHitDamage
from app.domain.progression import ProgressionCombatFeatures
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)
_PROTECTED_TYPES = ["aberration", "celestial", "elemental", "fey", "fiend", "undead"]
_ABILITIES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")


def _attack(weapon_id: str, strength_modifier: int) -> WeaponAttack:
    weapon = build_longsword() if weapon_id == "longsword" else build_weapon(weapon_id)
    return WeaponAttack(
        id=f"aurelia-{weapon_id}", weapon=weapon,
        attack_bonus=2 + strength_modifier, damage_bonus=strength_modifier,
        attack_ability="strength", attack_ability_modifier=strength_modifier,
    )


def _divine_favor_2024() -> DefensiveSpellAction:
    return DefensiveSpellAction(
        id="divine-favor", name="Divine Favor", level=1, action_cost="bonus_action",
        range_ft=0, duration_minutes=1, target_policy="self", concentration=False,
        priority=40,
        modifier_effects=[
            SpellModifierEffect(kind="bonus-damage", dice_count=1, dice_size=4, damage_type="radiant"),
        ],
        animation="divine-favor", source="D&D Beyond Basic Rules 2024: Divine Favor",
    )


def _protection_from_evil_and_good_2024() -> DefensiveSpellAction:
    save_advantage = [
        SpellModifierEffect(
            kind="saving-throw-advantage",
            save_ability=ability,
            source_creature_types=_PROTECTED_TYPES,
            required_effect_tags=[tag],
        )
        for tag in ("charm", "fear")
        for ability in _ABILITIES
    ]
    return DefensiveSpellAction(
        id="protection-from-evil-and-good",
        name="Protection from Evil and Good",
        level=1,
        action_cost="action",
        range_ft=5,
        duration_minutes=10,
        target_policy="friendly",
        target_count=1,
        concentration=True,
        priority=45,
        modifier_effects=[
            SpellModifierEffect(
                kind="attacks-against-disadvantage",
                source_creature_types=_PROTECTED_TYPES,
            ),
            SpellModifierEffect(
                kind="condition-immunity",
                condition_id="charmed",
                source_creature_types=_PROTECTED_TYPES,
            ),
            SpellModifierEffect(
                kind="condition-immunity",
                condition_id="frightened",
                source_creature_types=_PROTECTED_TYPES,
            ),
            *save_advantage,
        ],
        animation="protection",
        source="D&D Beyond Basic Rules 2024: Protection from Evil and Good",
    )


def _shield_of_faith_2024() -> DefensiveSpellAction:
    return DefensiveSpellAction(
        id="shield-of-faith",
        name="Shield of Faith",
        level=1,
        action_cost="bonus_action",
        range_ft=60,
        duration_minutes=10,
        target_policy="friendly",
        target_count=1,
        concentration=True,
        priority=50,
        modifier_effects=[SpellModifierEffect(kind="armor-class", flat_bonus=2)],
        animation="shield",
        source="D&D Beyond Basic Rules 2024: Shield of Faith",
    )


def _sacred_weapon_2024(charisma_modifier: int) -> AttackActionWeaponBuff:
    return AttackActionWeaponBuff(
        id="sacred-weapon",
        name="Sacred Weapon",
        resource_id="channel-divinity",
        resource_cost=1,
        weapon_id="longsword",
        duration_rounds=100,
        attack_roll_bonus=max(1, charisma_modifier),
        damage_type_choice=DamageType.RADIANT,
        source_is_magical=True,
        animation="bless",
    )


def _progression(level: int) -> ProgressionCombatFeatures:
    return ProgressionCombatFeatures(
        resource_backed_post_hit_damage=(
            ResourceBackedPostHitDamage(
                source_id="divine-smite-2024", source_name="Divine Smite",
                trigger_attack_ids=["aurelia-longsword"], action_cost="bonus_action",
                free_resource_id="paladins-smite-free-cast",
                printed_spell_level=1, max_slot_level=5,
                base_dice_count=2, dice_per_slot_above=1, dice_size=8,
                damage_type="radiant",
                bonus_target_creature_types=["fiend", "undead"],
                bonus_target_dice_count=1, doubles_on_critical=True,
            )
            if level >= 2 else None
        ),
    )


def _resources(level: int) -> list[ResourceDefinition]:
    resources = [
        ResourceDefinition(id="lay-on-hands", name="Lay On Hands", max_uses=5 * level),
        ResourceDefinition(
            id="spell-slot-1",
            name="Level 1 Spell Slot",
            max_uses=3 if level >= 3 else 2,
        ),
    ]
    if level >= 2:
        resources.append(ResourceDefinition(
            id="paladins-smite-free-cast", name="Paladin's Smite: Free Cast", max_uses=1,
        ))
    if level >= 3:
        resources.append(ResourceDefinition(
            id="channel-divinity", name="Channel Divinity", max_uses=2,
        ))
    return resources


def build_aurelia_brightshield_2024(level: int = 1) -> CombatantTemplate:
    """Build certified 2024 Aurelia through Paladin level 3."""
    try:
        if level not in {1, 2, 3}:
            raise ValueError("The current 2024 Paladin runtime tranche supports levels 1-3 only.")
        profile = build_aurelia_brightshield_2024_profile(level)
        scores = profile.final_ability_scores
        if scores is None:
            raise ValueError("2024 Aurelia profile is missing final ability scores.")
        strength = scores.modifier("strength")
        charisma = scores.modifier("charisma")
        pb = 2
        return CombatantTemplate(
            id=canonical_template_id("paladin", level),
            name=HERO_BY_CLASS["paladin"].hero_name, archetype="Paladin",
            level=level, kind="character", ruleset="2024", creature_type="humanoid",
            ability_scores=scores, armor_class=18 + int(level >= 2),
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=30, initiative_bonus=scores.modifier("dexterity"),
            starts_with_heroic_inspiration=True,
            weapon_attack=_attack("longsword", strength),
            alternate_weapon_attacks=[_attack("javelin", strength)],
            healing_actions=[
                HealingAction(
                    id="lay-on-hands-heal", name="Lay On Hands", action_cost="bonus_action",
                    range_ft=5, target_mode="self_or_ally", dice_count=0,
                    healing_bonus=5 * level, resource_id="lay-on-hands",
                    resource_cost=5 * level, animation="healing",
                ),
                build_cure_wounds(charisma),
            ],
            condition_removal_actions=[ConditionRemovalAction(
                id="lay-on-hands-poison", name="Lay On Hands", action_cost="bonus_action",
                range_ft=5, target_mode="self_or_ally", removable_conditions=["poisoned"],
                max_conditions_per_use=1, resource_costs_per_condition={"lay-on-hands": 5},
            )],
            defensive_spell_actions=[
                _divine_favor_2024(),
                *([BLESS.model_copy(deep=True)] if level >= 2 else []),
                *(
                    [_protection_from_evil_and_good_2024(), _shield_of_faith_2024()]
                    if level >= 3 else []
                ),
            ],
            attack_action_weapon_buffs=[
                _sacred_weapon_2024(charisma)
            ] if level >= 3 else [],
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("wisdom", "charisma")),
            skill_bonuses={
                "athletics": strength + pb, "intimidation": charisma + pb,
                "insight": scores.modifier("wisdom") + pb, "persuasion": charisma + pb,
                "perception": scores.modifier("wisdom") + pb,
                "acrobatics": scores.modifier("dexterity") + pb,
                "medicine": scores.modifier("wisdom") + pb,
                "religion": scores.modifier("intelligence") + pb,
            },
            combat_traits=[CombatTrait.SAVAGE_ATTACKER],
            progression_features=_progression(level),
            weapon_masteries=["longsword", "javelin"],
            fighting_style="Defense" if level >= 2 else None,
            fighting_styles=["Defense"] if level >= 2 else [],
            wearing_heavy_armor=True, wearing_metal_armor=True,
            visual=VisualLoadout(armor="chain-mail", main_hand="longsword", off_hand="shield"),
            resources=_resources(level),
            source=(
                f"D&D Beyond Basic Rules 2024: Paladin {level}, Human, Soldier, "
                "Cure Wounds, Divine Favor, "
                + ("Bless, Divine Smite, " if level >= 2 else "")
                + (
                    "Sacred Weapon, Protection from Evil and Good, Shield of Faith, "
                    if level >= 3 else ""
                )
                + "Longsword, Javelin"
            ),
        )
    except Exception:
        logger.exception("Failed to build 2024 Aurelia Brightshield at level %s.", level)
        raise

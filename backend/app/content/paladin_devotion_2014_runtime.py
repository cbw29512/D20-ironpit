from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.cleric_life_domain import AID
from app.content.paladin_devotion_2014_attacks import build_extra_attack, build_javelin_attack, build_longsword_attack
from app.content.paladin_devotion_2014_spells import (
    beacon_of_hope_2014, dispel_magic_2014, lesser_restoration_2014,
    protection_from_evil_and_good_2014, sanctuary_2014,
)
from app.content.spell_effects import BLESS, SHIELD_OF_FAITH
from app.domain.actions import ConditionRemovalAction, HealingAction
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)
_SLOTS = {
    1: (), 2: (2,), 3: (3,), 4: (3,), 5: (4, 2),
    6: (4, 2), 7: (4, 3), 8: (4, 3), 9: (4, 3, 2), 10: (4, 3, 2),
}


def _scores(level: int) -> AbilityScores:
    strength = 16 + (2 if level >= 4 else 0)
    charisma = 15 + (2 if level >= 8 else 0)
    return AbilityScores(
        strength=strength,
        dexterity=11,
        constitution=14,
        intelligence=9,
        wisdom=13,
        charisma=charisma,
    )


def _resources(level: int) -> list[ResourceDefinition]:
    resources = [ResourceDefinition(id="lay-on-hands", name="Lay on Hands", max_uses=5 * level)]
    for spell_level, uses in enumerate(_SLOTS[level], start=1):
        resources.append(ResourceDefinition(
            id=f"spell-slot-{spell_level}", name=f"Level {spell_level} Spell Slot", max_uses=uses,
        ))
    if level >= 3:
        resources.append(ResourceDefinition(id="channel-divinity", name="Channel Divinity", max_uses=1))
    return resources


def _healing_actions(level: int, charisma_modifier: int) -> list[HealingAction]:
    actions = [HealingAction(
        id="lay-on-hands-heal", name="Lay on Hands", action_cost="action", range_ft=5,
        target_mode="self_or_ally", dice_count=0, healing_bonus=5 * level,
        resource_id="lay-on-hands", resource_cost=5 * level, animation="healing",
    )]
    if level >= 2:
        actions.append(HealingAction(
            id="cure-wounds", name="Cure Wounds", action_cost="action", range_ft=5,
            target_mode="self_or_ally", dice_count=1, dice_size=8, healing_bonus=charisma_modifier,
            resource_id="spell-slot-1", resource_cost=1, animation="healing",
        ))
    return actions


def _condition_removal_actions(level: int) -> list[ConditionRemovalAction]:
    actions = [ConditionRemovalAction(
        id="lay-on-hands-poison", name="Lay on Hands", action_cost="action", range_ft=5,
        target_mode="self_or_ally", removable_conditions=["poisoned"], max_conditions_per_use=1,
        resource_costs_per_condition={"lay-on-hands": 5}, animation="condition-removal",
    )]
    if level >= 5:
        actions.append(lesser_restoration_2014())
    return actions


def _defensive_spells(level: int, charisma_modifier: int):
    if level < 2:
        return []
    source = "D&D SRD 5.1 (2014): Paladin spell list"
    actions = [
        BLESS.model_copy(update={"source": source}),
        SHIELD_OF_FAITH.model_copy(update={"source": source}),
    ]
    if level >= 3:
        actions.extend([
            protection_from_evil_and_good_2014(),
            sanctuary_2014(8 + proficiency_bonus(level) + charisma_modifier),
        ])
    if level >= 9:
        actions.append(beacon_of_hope_2014())
    if level >= 10:
        actions.append(AID.model_copy(update={"source": source}))
    return actions


def _skill_bonuses(level: int, scores: AbilityScores) -> dict[str, int]:
    pb = proficiency_bonus(level)
    return {
        "athletics": scores.modifier("strength") + pb,
        "insight": scores.modifier("wisdom") + pb,
        "history": scores.modifier("intelligence") + pb,
        "persuasion": scores.modifier("charisma") + pb,
    }


def build_aurelia_brightshield_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 11):
            raise ValueError("2014 Devotion Paladin certification covers levels 1 through 10.")
        scores = _scores(level)
        charisma_modifier = scores.modifier("charisma")
        aura_bonus = charisma_modifier if level >= 6 else 0
        saves = saving_throw_bonuses(scores, level, ("wisdom", "charisma"))
        if aura_bonus:
            saves = {ability: bonus + aura_bonus for ability, bonus in saves.items()}
        immunities = [condition for minimum, condition in ((7, "charmed"), (10, "frightened")) if level >= minimum]
        return CombatantTemplate(
            id=f"aurelia-brightshield-2014-l{level}", name="Aurelia Brightshield",
            archetype="Paladin", level=level, kind="character", ruleset="2014",
            ability_scores=scores, armor_class=18 + int(level >= 2),
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=30, initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=build_longsword_attack(level, scores),
            alternate_weapon_attacks=[build_javelin_attack(level, scores)],
            attack_action=build_extra_attack(level),
            defensive_spell_actions=_defensive_spells(level, charisma_modifier),
            healing_actions=_healing_actions(level, charisma_modifier),
            condition_removal_actions=_condition_removal_actions(level),
            effect_removal_actions=[dispel_magic_2014()] if level >= 9 else [],
            saving_throw_bonuses=saves, skill_bonuses=_skill_bonuses(level, scores),
            weapon_masteries=[], fighting_style="Defense" if level >= 2 else None,
            fighting_styles=["Defense"] if level >= 2 else [], condition_immunities=immunities,
            wearing_heavy_armor=True, resources=_resources(level),
            progression_features=ProgressionCombatFeatures(
                divine_smite_2014=level >= 2,
                turn_unholy_2014=level >= 3,
                sacred_weapon_2014_bonus=charisma_modifier if level >= 3 else 0,
                aura_of_protection_2014_bonus=aura_bonus,
                aura_of_devotion_2014=level >= 7,
                aura_of_courage_2014=level >= 10,
            ),
            visual=VisualLoadout(armor="chain-mail", main_hand="longsword", off_hand="shield"),
            source="D&D SRD 5.1 (2014): Paladin, Oath of Devotion; Basic Rules 2014: Human, Noble, Equipment",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Aurelia Brightshield at level %s", level)
        raise

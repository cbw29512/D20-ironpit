from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.paladin_devotion_2014_attacks import build_extra_attack, build_javelin_attack, build_longsword_attack
from app.content.paladin_devotion_2014_level14 import cleansing_touch_2014
from app.content.paladin_devotion_2014_level15 import purity_of_spirit_2014
from app.content.paladin_devotion_2014_level17 import flame_strike_2014
from app.content.paladin_devotion_2014_spells import (
    build_paladin_condition_removal_actions_2014,
    build_paladin_defensive_spells_2014,
    build_paladin_healing_actions_2014,
    dispel_magic_2014,
)
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, DamageType, OnHitDamage, ResourceDefinition, VisualLoadout
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)
_SLOTS = {
    1: (), 2: (2,), 3: (3,), 4: (3,), 5: (4, 2),
    6: (4, 2), 7: (4, 3), 8: (4, 3), 9: (4, 3, 2), 10: (4, 3, 2),
    11: (4, 3, 3), 12: (4, 3, 3), 13: (4, 3, 3, 1), 14: (4, 3, 3, 1),
    15: (4, 3, 3, 2), 16: (4, 3, 3, 2), 17: (4, 3, 3, 3, 1), 18: (4, 3, 3, 3, 1),
}


def _scores(level: int) -> AbilityScores:
    strength = 16 + (2 if level >= 4 else 0) + (2 if level >= 12 else 0)
    charisma = 15 + (2 if level >= 8 else 0) + (2 if level >= 16 else 0)
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
    if level >= 14:
        resources.append(ResourceDefinition(
            id="cleansing-touch",
            name="Cleansing Touch",
            max_uses=_scores(level).modifier("charisma"),
        ))
    return resources


def _skill_bonuses(level: int, scores: AbilityScores) -> dict[str, int]:
    pb = proficiency_bonus(level)
    return {
        "athletics": scores.modifier("strength") + pb,
        "insight": scores.modifier("wisdom") + pb,
        "history": scores.modifier("intelligence") + pb,
        "persuasion": scores.modifier("charisma") + pb,
    }


def _improved_divine_smite(level: int) -> list[OnHitDamage]:
    if level < 11:
        return []
    return [OnHitDamage(
        source="Improved Divine Smite",
        dice_count=1,
        dice_size=8,
        damage_type=DamageType.RADIANT,
    )]


def build_aurelia_brightshield_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 19):
            raise ValueError("2014 Devotion Paladin runtime covers levels 1 through 18.")
        scores = _scores(level)
        charisma_modifier = scores.modifier("charisma")
        aura_bonus = charisma_modifier if level >= 6 else 0
        aura_radius = 30 if level >= 18 else (10 if level >= 6 else 0)
        saves = saving_throw_bonuses(scores, level, ("wisdom", "charisma"))
        longsword = build_longsword_attack(level, scores).model_copy(
            update={"on_hit_damage": _improved_divine_smite(level)},
        )
        javelin = build_javelin_attack(level, scores).model_copy(
            update={"on_hit_damage": _improved_divine_smite(level)},
        )
        return CombatantTemplate(
            id=f"aurelia-brightshield-2014-l{level}", name="Aurelia Brightshield",
            archetype="Paladin", level=level, kind="character", ruleset="2014",
            ability_scores=scores, armor_class=18 + int(level >= 2),
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=30, initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=longsword,
            alternate_weapon_attacks=[javelin],
            attack_action=build_extra_attack(level),
            passive_modifier_grants=purity_of_spirit_2014() if level >= 15 else [],
            defensive_spell_actions=build_paladin_defensive_spells_2014(level, charisma_modifier),
            spell_save_actions=[flame_strike_2014(level, charisma_modifier)] if level >= 17 else [],
            healing_actions=build_paladin_healing_actions_2014(level, charisma_modifier),
            condition_removal_actions=build_paladin_condition_removal_actions_2014(level),
            effect_removal_actions=(
                [cleansing_touch_2014(), dispel_magic_2014()]
                if level >= 14
                else ([dispel_magic_2014()] if level >= 9 else [])
            ),
            saving_throw_bonuses=saves, skill_bonuses=_skill_bonuses(level, scores),
            weapon_masteries=[], fighting_style="Defense" if level >= 2 else None,
            fighting_styles=["Defense"] if level >= 2 else [], condition_immunities=[],
            wearing_heavy_armor=True, resources=_resources(level),
            progression_features=ProgressionCombatFeatures(
                divine_smite_2014=level >= 2,
                turn_unholy_2014=level >= 3,
                sacred_weapon_2014_bonus=charisma_modifier if level >= 3 else 0,
                aura_of_protection_2014_bonus=aura_bonus,
                aura_radius_2014_ft=aura_radius,
                aura_of_devotion_2014=level >= 7,
                aura_of_courage_2014=level >= 10,
            ),
            visual=VisualLoadout(armor="chain-mail", main_hand="longsword", off_hand="shield"),
            source="D&D SRD 5.1 (2014): Paladin, Oath of Devotion; Basic Rules 2014: Human, Noble, Equipment",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Aurelia Brightshield at level %s", level)
        raise

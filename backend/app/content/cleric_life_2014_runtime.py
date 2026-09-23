from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.cleric_2014_spell_effects import (
    build_cure_wounds_2014,
    build_defensive_spells_2014,
    build_guiding_bolt_2014,
    build_healing_word_2014,
    build_inflict_wounds_2014,
    build_sacred_flame_2014,
)
from app.content.cleric_life_2014_progression import final_scores_2014
from app.content.weapon_catalog import build_weapon
from app.domain.models import CombatantTemplate, DamageType, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_ALL_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def _warhammer(level: int, scores) -> WeaponAttack:
    weapon = build_weapon("warhammer").model_copy(update={"mastery_property": None})
    modifier = scores.modifier("strength")
    return WeaponAttack(
        id="seraphine-2014-warhammer",
        weapon=weapon,
        attack_bonus=proficiency_bonus(level) + modifier,
        damage_bonus=modifier,
        attack_ability="strength",
        attack_ability_modifier=modifier,
    )


def _skills(level: int, scores) -> dict[str, int]:
    pb = proficiency_bonus(level)
    return {
        "insight": scores.modifier("wisdom") + pb,
        "religion": scores.modifier("intelligence") + pb,
        "medicine": scores.modifier("wisdom") + pb,
        "persuasion": scores.modifier("charisma") + pb,
    }


def build_seraphine_dawnshield_2014(level: int = 1) -> CombatantTemplate:
    """Compile the same 2014 Life Cleric as cumulative levels are certified."""
    try:
        if level != 1:
            raise ValueError("2014 Life Cleric runtime is currently certified only at level 1.")
        scores = final_scores_2014(level)
        wisdom = scores.modifier("wisdom")
        pb = proficiency_bonus(level)
        spell_attack = pb + wisdom
        save_dc = 8 + pb + wisdom
        progression = ProgressionCombatFeatures(
            saving_throw_advantage_grants=[
                SavingThrowAdvantageGrant(
                    source_id="dwarven-resilience",
                    source_name="Dwarven Resilience",
                    abilities=list(_ALL_ABILITIES),
                    required_effect_tags=["poison"],
                )
            ],
        )
        return CombatantTemplate(
            id="seraphine-dawnshield-2014-l1",
            name="Seraphine Dawnshield",
            archetype="Cleric",
            level=1,
            kind="character",
            ruleset="2014",
            ability_scores=scores,
            armor_class=16,
            max_hp=fixed_hit_points(1, 8, scores.modifier("constitution")) + 1,
            speed_ft=25,
            initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=_warhammer(level, scores),
            spell_save_actions=[build_sacred_flame_2014(save_dc, level)],
            spell_attack_actions=[
                build_guiding_bolt_2014(spell_attack),
                build_inflict_wounds_2014(spell_attack),
            ],
            defensive_spell_actions=build_defensive_spells_2014(),
            healing_actions=[
                build_cure_wounds_2014(wisdom),
                build_healing_word_2014(wisdom),
            ],
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("wisdom", "charisma")),
            skill_bonuses=_skills(level, scores),
            damage_resistances=[DamageType.POISON],
            wearing_heavy_armor=False,
            weapon_masteries=[],
            resources=[
                ResourceDefinition(id="spell-slot-1", name="Level 1 Spell Slot", max_uses=2),
            ],
            progression_features=progression,
            visual=VisualLoadout(
                armor="scale-mail", main_hand="warhammer", off_hand="shield", body_style="hill-dwarf",
            ),
            source=(
                "D&D Basic Rules 2014: Hill Dwarf, Acolyte, Cleric, Life Domain, "
                "Equipment, Cleric Spells"
            ),
        )
    except Exception:
        logger.exception("Failed to compile 2014 Seraphine Dawnshield at level %s.", level)
        raise

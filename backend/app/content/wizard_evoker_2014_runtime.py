from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
from app.content.shared_invisibility_spells_2014 import greater_invisibility_2014
from app.content.sorcerer_draconic_2014_spell_support import false_life_2014
from app.content.warlock_2014_spells import circle_of_death_2014, finger_of_death_2014
from app.content.wizard_2014_progression import wizard_2014_level
from app.content.wizard_evoker_2014_profile import build_elian_starweaver_2014_profile
from app.content.wizard_evoker_2014_runtime_support import (
    build_wizard_evoker_features,
    build_wizard_resources,
    build_wizard_spell_actions,
    build_wizard_weapon,
)
from app.domain.actions import HpThresholdConditionAction, HpThresholdInstantDeathAction
from app.domain.models import CombatantTemplate, VisualLoadout

logger = logging.getLogger(__name__)


def build_elian_starweaver_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Elian runtime currently covers levels 1 through 20.")
        profile = build_elian_starweaver_2014_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        intelligence = scores.modifier("intelligence")
        dexterity = scores.modifier("dexterity")
        save_dc = 8 + pb + intelligence
        row = wizard_2014_level(level)
        spells = build_wizard_spell_actions(level, pb + intelligence, save_dc, intelligence)

        circle = circle_of_death_2014(save_dc).model_copy(
            update={"resource_id": "spell-slot-6", "resource_cost": 1}
        )
        finger = finger_of_death_2014(save_dc).model_copy(
            update={"resource_id": "spell-slot-7", "resource_cost": 1}
        )
        return CombatantTemplate(
            id=profile.template_id,
            name=profile.character_name,
            archetype="Wizard",
            level=level,
            kind="character",
            ruleset="2014",
            ability_scores=scores,
            armor_class=10 + dexterity,
            max_hp=fixed_hit_points(level, 6, scores.modifier("constitution")),
            speed_ft=30,
            movement_modes={"walk_ft": 30},
            initiative_bonus=dexterity,
            weapon_attack=build_wizard_weapon(level, scores),
            spell_attack_actions=spells.attacks,
            auto_hit_spell_actions=spells.auto_hits,
            spell_save_actions=spells.saves,
            saving_throw_actions=[
                *([circle] if level >= 11 else []),
                *([finger] if level >= 13 else []),
            ],
            hp_threshold_condition_actions=[
                *([HpThresholdConditionAction(
                    id="power-word-stun", name="Power Word Stun", action_cost="action",
                    range_ft=60, max_current_hp=150, condition_id="stunned",
                    repeat_save_ability="constitution", repeat_save_dc=save_dc,
                    repeat_save_timing="target_turn_end", resource_id="spell-slot-8",
                    resource_cost=1, magical_effect=True, animation="spell-condition",
                )] if level >= 15 else []),
            ],
            hp_threshold_instant_death_actions=[
                *([HpThresholdInstantDeathAction(
                    id="power-word-kill", name="Power Word Kill", action_cost="action",
                    range_ft=60, max_current_hp=100, resource_id="spell-slot-9",
                    resource_cost=1, magical_effect=True, animation="instant-death",
                )] if level >= 17 else []),
            ],
            defensive_spell_actions=[
                false_life_2014(),
                *([greater_invisibility_2014()] if level >= 7 else []),
            ],
            effect_removal_actions=[dispel_magic_2014("intelligence")] if level >= 6 else [],
            progression_features=build_wizard_evoker_features(level),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("intelligence", "wisdom")),
            skill_bonuses={
                "arcana": intelligence + pb,
                "history": intelligence + pb,
                "investigation": intelligence + pb,
                "insight": scores.modifier("wisdom") + pb,
            },
            resources=build_wizard_resources(row.spell_slots, level),
            weapon_masteries=[],
            visual=VisualLoadout(armor="unarmored", main_hand="arcane-focus", body_style="humanoid"),
            source="D&D Basic Rules 2014: Human; Sage; Wizard; School of Evocation; Equipment",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Elian Starweaver at level %s.", level)
        raise

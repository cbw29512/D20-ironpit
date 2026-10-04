from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.canonical_hero_policy import canonical_template_id
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.ranger_hunter_2024_features import (
    build_ranger_2024_progression,
    superior_hunters_defense_2024,
)
from app.content.ranger_hunter_2024_profile import build_rowan_ashtrail_2024_profile
from app.content.ranger_hunter_2024_resources import build_rowan_2024_resources
from app.content.ranger_hunter_2024_runtime_support import (
    build_rowan_2024_attack,
    build_rowan_2024_attack_action,
    build_rowan_2024_marks,
    build_rowan_2024_spell_actions,
    natures_veil_2024,
    ranger_2024_skill_bonuses,
)
from app.domain.models import CombatantTemplate, VisualLoadout

logger = logging.getLogger(__name__)


def build_rowan_ashtrail_2024(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Rowan runtime currently certifies levels 1 through 20.")
        profile = build_rowan_ashtrail_2024_profile(level)
        scores = profile.final_ability_scores
        dexterity = scores.modifier("dexterity")
        wisdom = scores.modifier("wisdom")
        pb = proficiency_bonus(level)
        armor = get_armor("studded-leather")
        speed = 45 if level >= 6 else 35
        marks, ensnaring = build_rowan_2024_marks(level, 8 + pb + wisdom)
        defensive, healing, removal, dispel = build_rowan_2024_spell_actions(level, wisdom)
        longbow = build_rowan_2024_attack("longbow", dexterity, level)
        shortsword = build_rowan_2024_attack("shortsword", dexterity, level)
        scimitar = build_rowan_2024_attack("scimitar", dexterity, level)
        return CombatantTemplate(
            id=canonical_template_id("ranger", level),
            name=HERO_BY_CLASS["ranger"].hero_name,
            archetype="Ranger",
            level=level,
            kind="character",
            ruleset="2024",
            creature_type="humanoid",
            ability_scores=scores,
            armor_class=compile_worn_armor_class(
                armor.base_ac, armor.category, dexterity, [],
                wielding_shield=False, shield_trained=True,
            ),
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=speed,
            movement_modes={"walk_ft": speed, "climb_ft": speed if level >= 6 else 0,
                            "swim_ft": speed if level >= 6 else 0},
            initiative_bonus=dexterity + pb,
            blindsight_ft=30 if level >= 18 else 0,
            weapon_attack=longbow,
            alternate_weapon_attacks=[shortsword, scimitar],
            attack_action=build_rowan_2024_attack_action(level),
            targeted_concentration_damage_actions=marks,
            post_hit_save_condition_spells=ensnaring,
            defensive_spell_actions=defensive,
            healing_actions=healing,
            condition_removal_actions=removal,
            effect_removal_actions=dispel,
            timed_self_buff_actions=natures_veil_2024(level),
            incoming_damage_type_resistance_reaction=superior_hunters_defense_2024(level),
            progression_features=build_ranger_2024_progression(level),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("strength", "dexterity")),
            skill_bonuses=ranger_2024_skill_bonuses(scores, level),
            weapon_masteries=["longbow", "shortsword"],
            fighting_style="Archery" if level >= 2 else None,
            fighting_styles=["Archery"] if level >= 2 else [],
            resources=build_rowan_2024_resources(level),
            visual=VisualLoadout(armor="studded-leather", main_hand="longbow", body_style="humanoid"),
            source=(
                "D&D Beyond Basic Rules 2024: Wood Elf; Outlander; Ranger; Hunter; "
                "Alert; Equipment"
            ),
        )
    except Exception:
        logger.exception("Failed to compile 2024 Rowan Ashtrail at level %s.", level)
        raise

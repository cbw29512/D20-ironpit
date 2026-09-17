from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.rogue_thief_2014_profile import build_mara_quickstep_2014_profile

logger = logging.getLogger(__name__)


def build_mara_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        source = build_mara_quickstep_2014_profile(level)
        scores = source.final_ability_scores; pb = proficiency_bonus(level)
        acrobatics_pb = 2 * pb if level >= 6 else pb
        deception_pb = 2 * pb if level >= 6 else pb
        return PregenCombatProfile(
            template_id=source.template_id, archetype="Rogue", level=level, abilities=scores,
            save_proficiencies=("dexterity", "intelligence"), armor_class=11 + scores.modifier("dexterity"),
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")), speed_ft=30,
            skill_bonuses=(
                ("acrobatics", scores.modifier("dexterity") + acrobatics_pb),
                ("stealth", scores.modifier("dexterity") + 2 * pb),
                ("perception", scores.modifier("wisdom") + 2 * pb),
                ("deception", scores.modifier("charisma") + deception_pb),
            ),
            attacks=(
                AttackExpectation("rapier", "dexterity", 1, 8, "piercing", sneak_attack_eligible=True),
                AttackExpectation("shortbow", "dexterity", 1, 6, "piercing", normal_range_ft=80,
                                  long_range_ft=320, sneak_attack_eligible=True),
            ),
            weapon_masteries=(), resources=(), sneak_attack_d6=(level + 1) // 2,
            initiative_bonus=scores.modifier("dexterity"),
        )
    except Exception:
        logger.exception("Failed 2014 Mara combat profile at level %s", level)
        raise


def build_mara_2014_combat_profiles() -> list[PregenCombatProfile]:
    return [build_mara_2014_combat_profile(level) for level in range(1, 11)]

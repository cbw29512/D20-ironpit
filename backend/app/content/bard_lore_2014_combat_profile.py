from __future__ import annotations

import logging

from app.content.bard_lore_2014_profile import build_lyra_silverstring_2014_profile
from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.spell_slot_progression import spell_slot_resources

logger = logging.getLogger(__name__)


def build_lyra_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Lyra combat fingerprint covers levels 1 through 20.")
        source = build_lyra_silverstring_2014_profile(level)
        scores = source.final_ability_scores
        pb = proficiency_bonus(level)
        charisma = scores.modifier("charisma")
        dexterity = scores.modifier("dexterity")
        jack_bonus = pb // 2 if level >= 2 else 0
        resources = [
            ("bardic-inspiration", max(1, charisma)),
            *spell_slot_resources("bard", level).items(),
        ]
        return PregenCombatProfile(
            template_id=source.template_id,
            archetype="Bard",
            level=level,
            abilities=scores,
            save_proficiencies=("dexterity", "charisma"),
            armor_class=11 + dexterity,
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=30,
            skill_bonuses=(
                ("acrobatics", dexterity + pb),
                ("perception", scores.modifier("wisdom") + pb),
                ("performance", charisma + pb),
                ("persuasion", charisma + pb),
            ),
            attacks=(AttackExpectation("rapier", "dexterity", 1, 8, "piercing"),),
            weapon_masteries=(),
            resources=tuple(resources),
            initiative_bonus=dexterity + jack_bonus,
        )
    except Exception:
        logger.exception("Failed to compile Lyra's 2014 combat fingerprint at level %s.", level)
        raise


def build_lyra_2014_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_lyra_2014_combat_profile(level) for level in range(1, 21)]
    except Exception:
        logger.exception("Failed to compile Lyra's 2014 combat fingerprints.")
        raise

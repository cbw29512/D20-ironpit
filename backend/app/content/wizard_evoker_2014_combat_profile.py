from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.wizard_2014_progression import wizard_2014_level
from app.content.wizard_evoker_2014_profile import build_elian_starweaver_2014_profile

logger = logging.getLogger(__name__)


def build_elian_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Elian combat fingerprint currently covers levels 1 through 20.")
        profile = build_elian_starweaver_2014_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dexterity = scores.modifier("dexterity")
        intelligence = scores.modifier("intelligence")
        row = wizard_2014_level(level)
        resources = [
            (f"spell-slot-{spell_level}", uses)
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        ]
        if level >= 20:
            resources.extend([
                ("signature-spell-fireball", 1),
                ("signature-spell-lightning-bolt", 1),
            ])
        return PregenCombatProfile(
            template_id=profile.template_id,
            archetype="Wizard",
            level=level,
            abilities=scores,
            save_proficiencies=("intelligence", "wisdom"),
            armor_class=10 + dexterity,
            max_hp=fixed_hit_points(level, 6, scores.modifier("constitution")),
            speed_ft=30,
            skill_bonuses=(
                ("arcana", intelligence + pb),
                ("history", intelligence + pb),
                ("investigation", intelligence + pb),
                ("insight", scores.modifier("wisdom") + pb),
            ),
            attacks=(AttackExpectation(
                "dagger", "dexterity", 1, 4, "piercing",
            ),),
            weapon_masteries=(),
            resources=tuple(resources),
            initiative_bonus=dexterity,
        )
    except Exception:
        logger.exception("Failed to compile Elian's 2014 combat fingerprint at level %s.", level)
        raise


def build_elian_2014_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_elian_2014_combat_profile(level) for level in range(1, 21)]
    except Exception:
        logger.exception("Failed to compile Elian's 2014 combat fingerprints.")
        raise

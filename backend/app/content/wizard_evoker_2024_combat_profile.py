from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.wizard_combat_levels import WIZARD_COMBAT_LEVELS
from app.content.wizard_evoker_2024_profile import build_elian_starweaver_2024_profile

logger = logging.getLogger(__name__)


def build_elian_2024_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Elian combat fingerprint currently covers levels 1 through 20.")
        profile = build_elian_starweaver_2024_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dex = scores.modifier("dexterity")
        intel = scores.modifier("intelligence")
        wis = scores.modifier("wisdom")
        row = WIZARD_COMBAT_LEVELS[level]
        resources = [
            (f"spell-slot-{spell_level}", uses)
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        ]
        if level >= 19:
            resources.append(("boon-of-fate", 1))
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
            armor_class=10 + dex,
            max_hp=fixed_hit_points(level, 6, scores.modifier("constitution")),
            speed_ft=30,
            skill_bonuses=(
                ("arcana", intel + (pb * 2 if level >= 2 else pb)),
                ("history", intel + pb),
                ("investigation", intel + pb),
                ("insight", wis + pb),
                ("religion", intel + pb),
                ("medicine", wis + pb),
                ("nature", intel + pb),
                ("perception", wis + pb),
            ),
            attacks=(AttackExpectation("dagger", "dexterity", 1, 4, "piercing"),),
            weapon_masteries=(),
            resources=tuple(resources),
            initiative_bonus=dex,
        )
    except Exception:
        logger.exception("Failed to compile Elian's 2024 combat fingerprint at level %s.", level)
        raise


def build_elian_2024_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_elian_2024_combat_profile(level) for level in range(1, 21)]
    except Exception:
        logger.exception("Failed to compile Elian's 2024 combat fingerprints.")
        raise

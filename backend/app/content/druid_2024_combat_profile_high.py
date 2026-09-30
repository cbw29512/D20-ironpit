from __future__ import annotations

import logging

from app.content.druid_2024_combat_profile_endgame import build_thalen_2024_endgame_combat_profiles
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)


def build_thalen_2024_high_combat_profiles(
    abilities_l8: AbilityScores,
    attacks: tuple[AttackExpectation, ...],
) -> tuple[PregenCombatProfile, ...]:
    """Independent source-derived combat fingerprints for Druid levels 9–16."""
    try:
        abilities_l12 = abilities_l8.model_copy(update={"charisma": 18})
        high_skills = (
            ("athletics", 0), ("acrobatics", 0), ("nature", 10), ("survival", 9),
            ("insight", 9), ("religion", 5), ("perception", 9),
        )
        shared = {
            "archetype": "Druid",
            "save_proficiencies": ("intelligence", "wisdom"),
            "armor_class": 13,
            "speed_ft": 35,
            "skill_bonuses": high_skills,
            "attacks": attacks,
            "weapon_masteries": (),
            "initiative_bonus": 0,
        }
        ward = {
            "damage_resistances": ("fire",),
            "condition_immunities": ("poisoned",),
        }
        return (
            PregenCombatProfile(
                template_id="thalen-greenbough-l9", level=9, abilities=abilities_l8,
                max_hp=48,
                resources=(
                    ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
                    ("spell-slot-4", 3), ("spell-slot-5", 1), ("wild-shape", 3),
                    ("wild-resurgence-slot-restore", 1), ("natural-recovery-free-cast", 1),
                ),
                **shared,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l10", level=10, abilities=abilities_l8,
                max_hp=53,
                resources=(
                    ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
                    ("spell-slot-4", 3), ("spell-slot-5", 2), ("wild-shape", 3),
                    ("wild-resurgence-slot-restore", 1), ("natural-recovery-free-cast", 1),
                ),
                **shared, **ward,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l11", level=11, abilities=abilities_l8,
                max_hp=58,
                resources=(
                    ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
                    ("spell-slot-4", 3), ("spell-slot-5", 2), ("spell-slot-6", 1),
                    ("wild-shape", 3), ("wild-resurgence-slot-restore", 1),
                    ("natural-recovery-free-cast", 1),
                ),
                **shared, **ward,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l12", level=12, abilities=abilities_l12,
                max_hp=63,
                resources=(
                    ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
                    ("spell-slot-4", 3), ("spell-slot-5", 2), ("spell-slot-6", 1),
                    ("wild-shape", 3), ("wild-resurgence-slot-restore", 1),
                    ("natural-recovery-free-cast", 1),
                ),
                **shared, **ward,
            ),
            *build_thalen_2024_endgame_combat_profiles(abilities_l12, attacks),
        )
    except Exception:
        logger.exception("Failed to build high-level 2024 Thalen combat fingerprints.")
        raise

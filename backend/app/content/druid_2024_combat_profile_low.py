from __future__ import annotations

import logging

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)


def build_thalen_2024_low_combat_profiles(
    abilities: AbilityScores,
    abilities_l4: AbilityScores,
    abilities_l8: AbilityScores,
    attacks: tuple[AttackExpectation, ...],
) -> tuple[PregenCombatProfile, ...]:
    """Independent source-derived combat fingerprints for Druid levels 1–8."""
    try:
        skills = (
            ("athletics", 0), ("acrobatics", 0), ("nature", 6), ("survival", 5),
            ("insight", 5), ("religion", 3), ("perception", 5),
        )
        skills_l4 = (
            ("athletics", 0), ("acrobatics", 0), ("nature", 7), ("survival", 6),
            ("insight", 6), ("religion", 3), ("perception", 6),
        )
        shared = {
            "archetype": "Druid",
            "save_proficiencies": ("intelligence", "wisdom"),
            "armor_class": 13,
            "speed_ft": 35,
            "attacks": attacks,
            "weapon_masteries": (),
            "initiative_bonus": 0,
        }
        return (
            PregenCombatProfile(
                template_id="thalen-greenbough-l1", level=1, abilities=abilities,
                max_hp=8, skill_bonuses=skills, resources=(("spell-slot-1", 2),), **shared,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l2", level=2, abilities=abilities,
                max_hp=13, skill_bonuses=skills,
                resources=(("spell-slot-1", 3), ("wild-shape", 2)), **shared,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l3", level=3, abilities=abilities,
                max_hp=18, skill_bonuses=skills,
                resources=(("spell-slot-1", 4), ("spell-slot-2", 2), ("wild-shape", 2)), **shared,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l4", level=4, abilities=abilities_l4,
                max_hp=23, skill_bonuses=skills_l4,
                resources=(("spell-slot-1", 4), ("spell-slot-2", 3), ("wild-shape", 2)), **shared,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l5", level=5, abilities=abilities_l4,
                max_hp=28,
                skill_bonuses=(
                    ("athletics", 0), ("acrobatics", 0), ("nature", 8), ("survival", 7),
                    ("insight", 7), ("religion", 4), ("perception", 7),
                ),
                resources=(
                    ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 2),
                    ("wild-shape", 2), ("wild-resurgence-slot-restore", 1),
                ),
                **shared,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l6", level=6, abilities=abilities_l4,
                max_hp=33,
                skill_bonuses=(
                    ("athletics", 0), ("acrobatics", 0), ("nature", 8), ("survival", 7),
                    ("insight", 7), ("religion", 4), ("perception", 7),
                ),
                resources=(
                    ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
                    ("wild-shape", 3), ("wild-resurgence-slot-restore", 1),
                    ("natural-recovery-free-cast", 1),
                ),
                **shared,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l7", level=7, abilities=abilities_l4,
                max_hp=38,
                skill_bonuses=(
                    ("athletics", 0), ("acrobatics", 0), ("nature", 8), ("survival", 7),
                    ("insight", 7), ("religion", 4), ("perception", 7),
                ),
                resources=(
                    ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
                    ("spell-slot-4", 1), ("wild-shape", 3),
                    ("wild-resurgence-slot-restore", 1), ("natural-recovery-free-cast", 1),
                ),
                **shared,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l8", level=8, abilities=abilities_l8,
                max_hp=43,
                skill_bonuses=(
                    ("athletics", 0), ("acrobatics", 0), ("nature", 9), ("survival", 8),
                    ("insight", 8), ("religion", 4), ("perception", 8),
                ),
                resources=(
                    ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
                    ("spell-slot-4", 2), ("wild-shape", 3),
                    ("wild-resurgence-slot-restore", 1), ("natural-recovery-free-cast", 1),
                ),
                **shared,
            ),
        )
    except Exception:
        logger.exception("Failed to build low-level 2024 Thalen combat fingerprints.")
        raise

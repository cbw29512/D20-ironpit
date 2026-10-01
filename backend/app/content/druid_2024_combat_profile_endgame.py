from __future__ import annotations

import logging

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)

_HIGH_SKILLS = (
    ("athletics", 0), ("acrobatics", 0), ("nature", 11), ("survival", 10),
    ("insight", 10), ("religion", 6), ("perception", 10),
)
_LEVEL17_SKILLS = (
    ("athletics", 0), ("acrobatics", 0), ("nature", 12), ("survival", 11),
    ("insight", 11), ("religion", 7), ("perception", 11),
)
_LEVEL19_SKILLS = (
    ("athletics", 0), ("acrobatics", 0), ("nature", 13), ("survival", 11),
    ("insight", 11), ("religion", 8), ("perception", 11),
)
_WARD = {
    "damage_resistances": ("fire",),
    "condition_immunities": ("poisoned",),
}


def _profile(
    level: int,
    abilities: AbilityScores,
    max_hp: int,
    resources: tuple[tuple[str, int], ...],
    attacks: tuple[AttackExpectation, ...],
    skills: tuple[tuple[str, int], ...] = _HIGH_SKILLS,
) -> PregenCombatProfile:
    try:
        return PregenCombatProfile(
            template_id=f"thalen-greenbough-l{level}",
            archetype="Druid",
            level=level,
            abilities=abilities,
            save_proficiencies=("intelligence", "wisdom"),
            armor_class=13,
            max_hp=max_hp,
            speed_ft=35,
            skill_bonuses=skills,
            attacks=attacks,
            weapon_masteries=(),
            resources=resources,
            initiative_bonus=0,
            **_WARD,
        )
    except Exception:
        logger.exception("Failed to build 2024 Druid level %s combat fingerprint.", level)
        raise


def build_thalen_2024_endgame_combat_profiles(
    abilities_l12: AbilityScores,
    attacks: tuple[AttackExpectation, ...],
) -> tuple[PregenCombatProfile, ...]:
    """Independent Druid combat fingerprints for levels 13–20."""
    try:
        abilities_l16 = abilities_l12.model_copy(update={"charisma": 20})
        abilities_l19 = abilities_l16.model_copy(update={"intelligence": 14})
        l13_14 = (
            ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
            ("spell-slot-4", 3), ("spell-slot-5", 2), ("spell-slot-6", 1),
            ("spell-slot-7", 1), ("wild-shape", 3),
            ("wild-resurgence-slot-restore", 1), ("natural-recovery-free-cast", 1),
        )
        l15_16 = (
            ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
            ("spell-slot-4", 3), ("spell-slot-5", 2), ("spell-slot-6", 1),
            ("spell-slot-7", 1), ("spell-slot-8", 1), ("wild-shape", 3),
            ("wild-resurgence-slot-restore", 1), ("natural-recovery-free-cast", 1),
        )
        l17 = (
            ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
            ("spell-slot-4", 3), ("spell-slot-5", 2), ("spell-slot-6", 1),
            ("spell-slot-7", 1), ("spell-slot-8", 1), ("spell-slot-9", 1),
            ("wild-shape", 4), ("wild-resurgence-slot-restore", 1),
            ("natural-recovery-free-cast", 1),
        )
        l18 = (
            ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
            ("spell-slot-4", 3), ("spell-slot-5", 3), ("spell-slot-6", 1),
            ("spell-slot-7", 1), ("spell-slot-8", 1), ("spell-slot-9", 1),
            ("wild-shape", 4), ("wild-resurgence-slot-restore", 1),
            ("natural-recovery-free-cast", 1),
        )
        l19 = (
            ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
            ("spell-slot-4", 3), ("spell-slot-5", 3), ("spell-slot-6", 2),
            ("spell-slot-7", 1), ("spell-slot-8", 1), ("spell-slot-9", 1),
            ("wild-shape", 4), ("wild-resurgence-slot-restore", 1),
            ("natural-recovery-free-cast", 1), ("boon-of-fate", 1),
        )
        l20 = (
            ("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3),
            ("spell-slot-4", 3), ("spell-slot-5", 3), ("spell-slot-6", 2),
            ("spell-slot-7", 2), ("spell-slot-8", 1), ("spell-slot-9", 1),
            ("wild-shape", 4), ("wild-resurgence-slot-restore", 1),
            ("natural-recovery-free-cast", 1), ("boon-of-fate", 1),
            ("nature-magician-conversion", 1),
        )
        return (
            _profile(13, abilities_l12, 68, l13_14, attacks),
            _profile(14, abilities_l12, 73, l13_14, attacks),
            _profile(15, abilities_l12, 78, l15_16, attacks),
            _profile(16, abilities_l16, 83, l15_16, attacks),
            _profile(17, abilities_l16, 88, l17, attacks, _LEVEL17_SKILLS),
            _profile(18, abilities_l16, 93, l18, attacks, _LEVEL17_SKILLS),
            _profile(19, abilities_l19, 98, l19, attacks, _LEVEL19_SKILLS),
            _profile(20, abilities_l19, 103, l20, attacks, _LEVEL19_SKILLS),
        )
    except Exception:
        logger.exception("Failed to build endgame 2024 Thalen combat fingerprints.")
        raise

from __future__ import annotations

import logging

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)


def build_thalen_2024_combat_profiles() -> tuple[PregenCombatProfile, ...]:
    """Independent source-derived fingerprint for certified 2024 Druid levels."""
    try:
        abilities = AbilityScores(
            strength=10,
            dexterity=10,
            constitution=10,
            intelligence=13,
            wisdom=17,
            charisma=15,
        )
        skills = (
            ("athletics", 0), ("acrobatics", 0), ("nature", 6), ("survival", 5),
            ("insight", 5), ("religion", 3), ("perception", 5),
        )
        abilities_l4 = abilities.model_copy(update={"wisdom": 19})
        skills_l4 = (
            ("athletics", 0), ("acrobatics", 0), ("nature", 7), ("survival", 6),
            ("insight", 6), ("religion", 3), ("perception", 6),
        )
        attacks = (AttackExpectation("sickle", "strength", 1, 4, "slashing"),)
        return (
            PregenCombatProfile(
                template_id="thalen-greenbough-l1", archetype="Druid", level=1,
                abilities=abilities, save_proficiencies=("intelligence", "wisdom"),
                armor_class=13, max_hp=8, speed_ft=35, skill_bonuses=skills,
                attacks=attacks, weapon_masteries=(), resources=(("spell-slot-1", 2),),
                initiative_bonus=0,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l2", archetype="Druid", level=2,
                abilities=abilities, save_proficiencies=("intelligence", "wisdom"),
                armor_class=13, max_hp=13, speed_ft=35, skill_bonuses=skills,
                attacks=attacks, weapon_masteries=(),
                resources=(("spell-slot-1", 3), ("wild-shape", 2)), initiative_bonus=0,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l3", archetype="Druid", level=3,
                abilities=abilities, save_proficiencies=("intelligence", "wisdom"),
                armor_class=13, max_hp=18, speed_ft=35, skill_bonuses=skills,
                attacks=attacks, weapon_masteries=(),
                resources=(("spell-slot-1", 4), ("spell-slot-2", 2), ("wild-shape", 2)),
                initiative_bonus=0,
            ),
            PregenCombatProfile(
                template_id="thalen-greenbough-l4", archetype="Druid", level=4,
                abilities=abilities_l4, save_proficiencies=("intelligence", "wisdom"),
                armor_class=13, max_hp=23, speed_ft=35, skill_bonuses=skills_l4,
                attacks=attacks, weapon_masteries=(),
                resources=(("spell-slot-1", 4), ("spell-slot-2", 3), ("wild-shape", 2)),
                initiative_bonus=0,
            ),
        )
    except Exception:
        logger.exception("Failed to build 2024 Thalen combat fingerprint.")
        raise

from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.weapon_catalog import build_weapon
from app.content.wizard_evoker_2014_data import ability_scores
from app.content.wizard_evoker_2014_progression import wizard_evoker_2014_level
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)


def _attack(level: int) -> WeaponAttack:
    try:
        scores = ability_scores(level)
        dexterity = scores.modifier("dexterity")
        weapon = build_weapon("light-crossbow").model_copy(update={"mastery_property": None})
        return WeaponAttack(
            id="elian-2014-light-crossbow",
            weapon=weapon,
            attack_bonus=proficiency_bonus(level) + dexterity,
            damage_bonus=dexterity,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build Elian's light crossbow at level %s.", level)
        raise


def _resources(level: int) -> list[ResourceDefinition]:
    try:
        row = wizard_evoker_2014_level(level)
        return [
            ResourceDefinition(
                id=f"spell-slot-{spell_level}",
                name=f"Level {spell_level} Spell Slot",
                max_uses=uses,
            )
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        ]
    except Exception:
        logger.exception("Failed to compile Elian's resources at level %s.", level)
        raise


def _skills(level: int) -> dict[str, int]:
    try:
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        return {
            "arcana": scores.modifier("intelligence") + pb,
            "history": scores.modifier("intelligence") + pb,
            "insight": scores.modifier("wisdom") + pb,
            "investigation": scores.modifier("intelligence") + pb,
        }
    except Exception:
        logger.exception("Failed to compile Elian's skills at level %s.", level)
        raise


def build_elian_starweaver_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Evoker Wizard build support covers levels 1 through 20.")
        scores = ability_scores(level)
        return CombatantTemplate(
            id=f"elian-starweaver-2014-l{level}",
            name="Elian Starweaver",
            archetype="Wizard",
            level=level,
            kind="character",
            ruleset="2014",
            ability_scores=scores,
            armor_class=10 + scores.modifier("dexterity"),
            max_hp=fixed_hit_points(level, 6, scores.modifier("constitution")),
            speed_ft=30,
            initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=_attack(level),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("intelligence", "wisdom")),
            skill_bonuses=_skills(level),
            progression_features=ProgressionCombatFeatures(),
            resources=_resources(level),
            weapon_masteries=[],
            wearing_heavy_armor=False,
            visual=VisualLoadout(armor="unarmored", main_hand="light-crossbow", off_hand="arcane-focus"),
            source="D&D Basic Rules 2014: Human, Sage, Equipment; D&D SRD 5.1 (2014): Wizard, School of Evocation",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Elian Starweaver at level %s.", level)
        raise

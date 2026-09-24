from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.warlock_fiend_2014_data import ability_scores
from app.content.warlock_fiend_2014_progression import warlock_fiend_2014_level
from app.content.shared_spell_saves_2014 import fireball_2014, poison_spray_2014
from app.content.weapon_catalog import build_weapon
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)


def _attack(level: int) -> WeaponAttack:
    try:
        scores = ability_scores(level)
        dexterity = scores.modifier("dexterity")
        weapon = build_weapon("light-crossbow").model_copy(update={"mastery_property": None})
        return WeaponAttack(
            id="varek-2014-light-crossbow", weapon=weapon,
            attack_bonus=proficiency_bonus(level) + dexterity,
            damage_bonus=dexterity,
            attack_ability="dexterity", attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build Varek's light crossbow at level %s.", level)
        raise


def _resources(level: int) -> list[ResourceDefinition]:
    try:
        row = warlock_fiend_2014_level(level)
        resources = [
            ResourceDefinition(
                id=f"spell-slot-{row.pact_slot_level}",
                name=f"Pact Magic Level {row.pact_slot_level} Slot",
                max_uses=row.pact_slots,
            )
        ]
        for spell_level in row.mystic_arcanum_levels:
            resources.append(ResourceDefinition(
                id=f"mystic-arcanum-{spell_level}",
                name=f"Mystic Arcanum Level {spell_level}",
                max_uses=1,
            ))
        return resources
    except Exception:
        logger.exception("Failed to compile Varek's resources at level %s.", level)
        raise


def _skills(level: int) -> dict[str, int]:
    try:
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        return {
            "arcana": scores.modifier("intelligence") + pb,
            "deception": scores.modifier("charisma") + pb,
            "intimidation": scores.modifier("charisma") + pb,
            "sleight-of-hand": scores.modifier("dexterity") + pb,
        }
    except Exception:
        logger.exception("Failed to compile Varek's skills at level %s.", level)
        raise


def build_varek_ashenmark_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Fiend Warlock build support covers levels 1 through 20.")
        scores = ability_scores(level)
        row = warlock_fiend_2014_level(level)
        spell_save_dc = 8 + proficiency_bonus(level) + scores.modifier("charisma")
        save_spells = [poison_spray_2014(spell_save_dc, level)]
        if level >= 5:
            # Fiend expanded spell choice, always compiled at the current Pact Magic slot level.
            save_spells.append(fireball_2014(spell_save_dc, row.pact_slot_level))
        return CombatantTemplate(
            id=f"varek-ashenmark-2014-l{level}", name="Varek Ashenmark",
            archetype="Warlock", level=level, kind="character", ruleset="2014",
            ability_scores=scores,
            armor_class=11 + scores.modifier("dexterity"),
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=30, initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=_attack(level),
            spell_save_actions=save_spells,
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("wisdom", "charisma")),
            skill_bonuses=_skills(level),
            progression_features=ProgressionCombatFeatures(),
            resources=_resources(level),
            weapon_masteries=[],
            wearing_heavy_armor=False,
            visual=VisualLoadout(armor="leather", main_hand="light-crossbow", off_hand="arcane-focus"),
            source="D&D Basic Rules 2014: Human, Charlatan, Equipment; D&D SRD 5.1 (2014): Warlock, The Fiend",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Varek Ashenmark at level %s.", level)
        raise

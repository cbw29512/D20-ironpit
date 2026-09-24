from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.sorcerer_draconic_2014_data import ability_scores
from app.content.sorcerer_draconic_2014_progression import sorcerer_draconic_2014_level
from app.content.shared_spell_attacks_2014 import fire_bolt_2014
from app.content.shared_spell_saves_2014 import disintegrate_2014, fireball_2014
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
            id="nyra-2014-light-crossbow", weapon=weapon,
            attack_bonus=proficiency_bonus(level) + dexterity,
            damage_bonus=dexterity,
            attack_ability="dexterity", attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build Nyra's light crossbow at level %s.", level)
        raise


def _resources(level: int) -> list[ResourceDefinition]:
    try:
        row = sorcerer_draconic_2014_level(level)
        resources = [
            ResourceDefinition(
                id=f"spell-slot-{spell_level}",
                name=f"Level {spell_level} Spell Slot",
                max_uses=uses,
            )
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        ]
        if row.sorcery_points:
            resources.append(ResourceDefinition(
                id="sorcery-points", name="Sorcery Points", max_uses=row.sorcery_points,
            ))
        return resources
    except Exception:
        logger.exception("Failed to compile Nyra's resources at level %s.", level)
        raise


def _skills(level: int) -> dict[str, int]:
    try:
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        return {
            "arcana": scores.modifier("intelligence") + pb,
            "medicine": scores.modifier("wisdom") + pb,
            "persuasion": scores.modifier("charisma") + pb,
            "religion": scores.modifier("intelligence") + pb,
        }
    except Exception:
        logger.exception("Failed to compile Nyra's skills at level %s.", level)
        raise


def build_nyra_emberveil_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Draconic Sorcerer build support covers levels 1 through 20.")
        scores = ability_scores(level)
        spell_attack_bonus = proficiency_bonus(level) + scores.modifier("charisma")
        spell_save_dc = 8 + proficiency_bonus(level) + scores.modifier("charisma")
        save_spells = []
        if level >= 5:
            save_spells.append(fireball_2014(spell_save_dc))
        if level >= 11:
            save_spells.append(disintegrate_2014(spell_save_dc))
        return CombatantTemplate(
            id=f"nyra-emberveil-2014-l{level}", name="Nyra Emberveil",
            archetype="Sorcerer", level=level, kind="character", ruleset="2014",
            ability_scores=scores,
            armor_class=13 + scores.modifier("dexterity"),
            max_hp=fixed_hit_points(level, 6, scores.modifier("constitution")) + level,
            speed_ft=30, initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=_attack(level),
            spell_attack_actions=[fire_bolt_2014(spell_attack_bonus, level)],
            spell_save_actions=save_spells,
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("constitution", "charisma")),
            skill_bonuses=_skills(level),
            progression_features=ProgressionCombatFeatures(),
            resources=_resources(level),
            weapon_masteries=[],
            wearing_heavy_armor=False,
            visual=VisualLoadout(armor="unarmored", main_hand="light-crossbow", off_hand="arcane-focus"),
            source="D&D Basic Rules 2014: Human, Hermit, Equipment; D&D SRD 5.1 (2014): Sorcerer, Draconic Bloodline",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Nyra Emberveil at level %s.", level)
        raise

from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.druid_land_2014_data import ability_scores
from app.content.druid_land_2014_progression import druid_land_2014_level
from app.content.shared_healing_spells_2014 import cure_wounds_2014
from app.content.shared_spell_attacks_2014 import produce_flame_2014
from app.content.shared_spell_saves_2014 import poison_spray_2014
from app.content.weapon_catalog import build_weapon
from app.domain.movement import DifficultTerrainBypassGrant
from app.domain.models import CombatantTemplate, DamageType, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import PassiveModifierGrant, ProgressionCombatFeatures
from app.domain.spell_modifiers import SpellModifierEffect

logger = logging.getLogger(__name__)


def _attack(level: int) -> WeaponAttack:
    try:
        scores = ability_scores(level)
        dexterity = scores.modifier("dexterity")
        weapon = build_weapon("scimitar").model_copy(update={"mastery_property": None})
        return WeaponAttack(
            id="thalen-2014-scimitar",
            weapon=weapon,
            attack_bonus=proficiency_bonus(level) + dexterity,
            damage_bonus=dexterity,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build Thalen's scimitar at level %s.", level)
        raise


def _resources(level: int) -> list[ResourceDefinition]:
    try:
        row = druid_land_2014_level(level)
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
        logger.exception("Failed to compile Thalen's resources at level %s.", level)
        raise


def _skills(level: int) -> dict[str, int]:
    try:
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        return {
            "arcana": scores.modifier("intelligence") + pb,
            "medicine": scores.modifier("wisdom") + pb,
            "nature": scores.modifier("intelligence") + pb,
            "perception": scores.modifier("wisdom") + pb,
        }
    except Exception:
        logger.exception("Failed to compile Thalen's skills at level %s.", level)
        raise


def build_thalen_greenbough_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Land Druid build support covers levels 1 through 20.")
        scores = ability_scores(level)
        spell_attack_bonus = proficiency_bonus(level) + scores.modifier("wisdom")
        spell_save_dc = 8 + proficiency_bonus(level) + scores.modifier("wisdom")
        return CombatantTemplate(
            id=f"thalen-greenbough-2014-l{level}",
            name="Thalen Greenbough",
            archetype="Druid",
            level=level,
            kind="character",
            ruleset="2014",
            ability_scores=scores,
            armor_class=13 + scores.modifier("dexterity"),
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=30,
            initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=_attack(level),
            spell_attack_actions=[produce_flame_2014(spell_attack_bonus, level)],
            spell_save_actions=[poison_spray_2014(spell_save_dc, level)],
            healing_actions=[cure_wounds_2014(scores.modifier("wisdom"))],
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("intelligence", "wisdom")),
            skill_bonuses=_skills(level),
            progression_features=ProgressionCombatFeatures(
                difficult_terrain_bypass_grants=(
                    [DifficultTerrainBypassGrant(
                        source_id="lands-stride",
                        source_name="Land's Stride",
                        scope="nonmagical",
                    )]
                    if level >= 6 else []
                ),
                passive_modifier_grants=(
                    [PassiveModifierGrant(
                        source_id="natures-ward",
                        source_name="Nature's Ward",
                        modifier_effects=[
                            SpellModifierEffect(
                                kind="condition-immunity",
                                condition_id="charmed",
                                source_creature_types=["elemental", "fey"],
                            ),
                            SpellModifierEffect(
                                kind="condition-immunity",
                                condition_id="frightened",
                                source_creature_types=["elemental", "fey"],
                            ),
                        ],
                    )]
                    if level >= 10 else []
                ),
            ),
            damage_immunities=[DamageType.POISON] if level >= 10 else [],
            condition_immunities=["poisoned"] if level >= 10 else [],
            resources=_resources(level),
            weapon_masteries=[],
            wearing_heavy_armor=False,
            visual=VisualLoadout(armor="leather", main_hand="scimitar", off_hand="wooden-shield"),
            source="D&D Basic Rules 2014: Human, Hermit, Equipment; D&D SRD 5.1 (2014): Druid, Circle of the Land",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Thalen Greenbough at level %s.", level)
        raise

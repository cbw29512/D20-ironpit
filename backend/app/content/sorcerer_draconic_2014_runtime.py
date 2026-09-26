from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.monster_equipment import build_light_crossbow
from app.content.sorcerer_2014_font_of_magic import font_of_magic_2014_actions
from app.content.sorcerer_2014_metamagic import distant_spell_2014, heightened_spell_2014
from app.content.paladin_devotion_2014_spells import dispel_magic_2014
from app.content.shared_invisibility_spells_2014 import greater_invisibility_2014
from app.content.sorcerer_2014_progression import sorcerer_2014_level
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_spells import burning_hands_2014, fire_bolt_2014, fireball_2014
from app.domain.models import CombatantTemplate, DamageType, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.spell_cast_effects import SpellCastTimedResistance
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def build_nyra_emberveil_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 17):
            raise ValueError("2014 Draconic Sorcerer runtime currently covers levels 1 through 16.")
        profile = build_nyra_emberveil_2014_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dex = scores.modifier("dexterity")
        cha = scores.modifier("charisma")
        crossbow = build_light_crossbow()
        weapon_attack = WeaponAttack(
            id="nyra-2014-light-crossbow", weapon=crossbow,
            attack_bonus=pb + dex, damage_bonus=dex,
            attack_ability="dexterity", attack_ability_modifier=dex,
        )
        row = sorcerer_2014_level(level)
        resources = [
            ResourceDefinition(id=f"spell-slot-{spell_level}", name=f"Spell Slot {spell_level}", max_uses=uses)
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        ]
        if row.sorcery_points:
            resources.append(ResourceDefinition(id="sorcery-points", name="Sorcery Points", max_uses=row.sorcery_points))
        return CombatantTemplate(
            id=profile.template_id, name=profile.character_name, archetype="Sorcerer",
            level=level, kind="character", ruleset="2014", ability_scores=scores,
            armor_class=13 + dex,
            max_hp=fixed_hit_points(level, 6, scores.modifier("constitution")) + level,
            speed_ft=30,
            movement_modes={"walk_ft": 30, "fly_ft": 30 if level >= 14 else 0},
            initiative_bonus=dex,
            weapon_attack=weapon_attack,
            spell_attack_actions=[fire_bolt_2014(pb + cha, level, cha if level >= 6 else 0)],
            spell_save_actions=[
                burning_hands_2014(8 + pb + cha, cha if level >= 6 else 0),
                *([fireball_2014(8 + pb + cha, cha if level >= 6 else 0)] if level >= 5 else []),
            ],
            spell_cast_timed_resistances=([
                SpellCastTimedResistance(
                    id="elemental-affinity-fire-resistance",
                    name="Elemental Affinity: Fire Resistance",
                    qualifying_damage_type=DamageType.FIRE,
                    resistance_damage_type=DamageType.FIRE,
                    resource_id="sorcery-points",
                    resource_cost=1,
                    duration_rounds=600,
                    priority=100,
                )
            ] if level >= 6 else []),
            defensive_spell_actions=([greater_invisibility_2014()] if level >= 7 else []),
            effect_removal_actions=([dispel_magic_2014()] if level >= 8 else []),
            resource_conversion_actions=(font_of_magic_2014_actions(level) if level >= 2 else []),
            spell_save_disadvantage_options=([heightened_spell_2014()] if level >= 3 else []),
            spell_range_modifiers=([distant_spell_2014()] if level >= 10 else []),
            progression_features=ProgressionCombatFeatures(
                saving_throw_advantage_grants=[
                    SavingThrowAdvantageGrant(
                        source_id="fey-ancestry", source_name="Fey Ancestry",
                        abilities=_ABILITIES, required_effect_tags=["charm"],
                    )
                ],
            ),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("constitution", "charisma")),
            skill_bonuses={
                "arcana": scores.modifier("intelligence") + pb,
                "persuasion": cha + pb,
                "perception": scores.modifier("wisdom") + pb,
                "stealth": dex + pb,
                "deception": cha + pb,
                "sleight-of-hand": dex + pb,
            },
            weapon_masteries=[],
            resources=resources,
            visual=VisualLoadout(armor="unarmored", main_hand="light-crossbow", body_style="humanoid"),
            source="D&D Basic Rules 2014: Half-Elf; Charlatan; Sorcerer; Draconic Bloodline; Equipment",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Nyra Emberveil at level %s.", level)
        raise

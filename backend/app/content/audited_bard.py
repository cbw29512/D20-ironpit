from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.audited_bard_profile import build_lyra_silverstring_profile
from app.content.bard_2024_cutting_words import build_cutting_words_2024
from app.content.bard_2024_inspiration import build_bardic_inspiration_2024
from app.content.bard_2024_spells import build_shatter_2024
from app.content.bard_combat_levels import BARD_COMBAT_LEVELS
from app.content.character_math import saving_throw_bonuses
from app.content.healing_spell_effects import build_cure_wounds, build_healing_word
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.weapon_catalog import build_weapon
from app.domain.combatants import ResourceDefinition
from app.domain.models import CombatantTemplate, VisualLoadout, WeaponAttack
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _dagger(level: int, dexterity_modifier: int) -> WeaponAttack:
    try:
        weapon = build_weapon("dagger").model_copy(update={"mastery_property": None})
        proficiency_bonus = BARD_COMBAT_LEVELS[level].proficiency_bonus
        return WeaponAttack(
            id="lyra-dagger",
            weapon=weapon,
            attack_bonus=proficiency_bonus + dexterity_modifier,
            damage_bonus=dexterity_modifier,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity_modifier,
        )
    except Exception:
        logger.exception("Failed to build Lyra's dagger attack at Bard level %s.", level)
        raise


def _resources(level: int) -> list[ResourceDefinition]:
    try:
        row = BARD_COMBAT_LEVELS[level]
        resources = [
            ResourceDefinition(
                id="bardic-inspiration",
                name="Bardic Inspiration",
                max_uses=row.bardic_inspiration_uses,
            ),
            ResourceDefinition(id="adrenaline-rush", name="Adrenaline Rush", max_uses=row.proficiency_bonus),
            ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
        ]
        resources.extend(
            ResourceDefinition(
                id=f"spell-slot-{spell_level}",
                name=f"Spell Slot {spell_level}",
                max_uses=uses,
            )
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        )
        return resources
    except Exception:
        logger.exception("Failed to build Lyra's resources at Bard level %s.", level)
        raise


def _skills(level: int, scores, proficiency_bonus: int) -> dict[str, int]:
    try:
        athletics = scores.modifier("strength")
        if level >= 3:
            athletics += proficiency_bonus
        elif level >= 2:
            athletics += proficiency_bonus // 2
        skills = {
            "athletics": athletics,
            "acrobatics": scores.modifier("dexterity") + proficiency_bonus * (2 if level >= 2 else 1),
            "perception": scores.modifier("wisdom") + proficiency_bonus,
            "performance": scores.modifier("charisma") + proficiency_bonus * (2 if level >= 2 else 1),
            "insight": scores.modifier("wisdom") + proficiency_bonus,
            "religion": scores.modifier("intelligence") + proficiency_bonus,
        }
        if level >= 3:
            skills.update({
                "deception": scores.modifier("charisma") + proficiency_bonus,
                "investigation": scores.modifier("intelligence") + proficiency_bonus,
            })
        return skills
    except Exception:
        logger.exception("Failed to compile Lyra's skill bonuses at Bard level %s.", level)
        raise


def build_lyra_silverstring_level(level: int) -> CombatantTemplate:
    """Compile the 2024 Lore Bard progression through level 3."""
    try:
        if level not in {1, 2, 3}:
            raise ValueError("2024 Lyra runtime currently supports Bard levels 1 through 3.")
        profile = build_lyra_silverstring_profile(level)
        row = BARD_COMBAT_LEVELS[level]
        scores = profile.final_ability_scores
        dexterity_modifier = scores.modifier("dexterity")
        charisma_modifier = scores.modifier("charisma")
        armor = get_armor("studded-leather")
        armor_class = compile_worn_armor_class(
            armor.base_ac,
            armor.category,
            dexterity_modifier,
            [],
            wielding_shield=False,
            shield_trained=False,
        )
        save_dc = 8 + row.proficiency_bonus + charisma_modifier
        return CombatantTemplate(
            id=profile.template_id,
            name=HERO_BY_CLASS["bard"].hero_name,
            archetype="Bard",
            level=level,
            kind="character",
            ability_scores=scores,
            armor_class=armor_class,
            max_hp=row.max_hp,
            speed_ft=30,
            initiative_bonus=dexterity_modifier,
            weapon_attack=_dagger(level, dexterity_modifier),
            healing_actions=[
                build_healing_word(charisma_modifier),
                build_cure_wounds(charisma_modifier),
            ],
            spell_save_actions=([build_shatter_2024(save_dc)] if level >= 3 else []),
            d20_bonus_die_actions=[build_bardic_inspiration_2024(level)],
            reaction_roll_penalty_actions=(
                [build_cutting_words_2024(level)] if level >= 3 else []
            ),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("dexterity", "charisma")),
            skill_bonuses=_skills(level, scores, row.proficiency_bonus),
            combat_traits=[CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE],
            resources=_resources(level),
            weapon_masteries=[],
            visual=VisualLoadout(
                armor=armor.id,
                main_hand="dagger",
                off_hand="lute",
                body_style="humanoid",
            ),
            source=(
                "D&D Beyond Basic Rules 2024: Bard, College of Lore, Acolyte, Orc, "
                "Bardic Inspiration, Cutting Words, Healing Word, Cure Wounds, Shatter, Equipment"
            ),
        )
    except Exception:
        logger.exception("Failed to compile 2024 Lyra Silverstring at level %s.", level)
        raise

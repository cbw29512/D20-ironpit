from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.bard_2014_countercharm import countercharm_2014
from app.content.bard_2014_cutting_words import cutting_words_2014
from app.content.bard_2014_inspiration import build_bardic_inspiration_2014
from app.content.bard_2014_initiative import build_bard_2014_initiative_refills
from app.content.bard_lore_2014_profile import build_lyra_silverstring_2014_profile
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.cleric_2014_level1_spells import bless_2014, cure_wounds_2014, healing_word_2014
from app.content.paladin_devotion_2014_spells import dispel_magic_2014
from app.content.shared_movement_spells_2014 import freedom_of_movement_2014
from app.content.shared_spells_2014 import lesser_restoration_2014, spiritual_weapon_2014
from app.content.weapon_catalog import build_weapon
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack

logger = logging.getLogger(__name__)


def _attack(level: int, scores) -> WeaponAttack:
    weapon = build_weapon("rapier").model_copy(update={"mastery_property": None})
    modifier = scores.modifier("dexterity")
    return WeaponAttack(
        id="lyra-2014-rapier",
        weapon=weapon,
        attack_bonus=proficiency_bonus(level) + modifier,
        damage_bonus=modifier,
        attack_ability="dexterity",
        attack_ability_modifier=modifier,
    )


def _resources(level: int, charisma_modifier: int) -> list[ResourceDefinition]:
    from app.content.bard_2014_progression import bard_2014_level

    row = bard_2014_level(level)
    resources = [
        ResourceDefinition(
            id="bardic-inspiration",
            name="Bardic Inspiration",
            max_uses=max(1, charisma_modifier),
        ),
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


def build_lyra_silverstring_2014(level: int) -> CombatantTemplate:
    """Compile the persistent 2014 College of Lore Bard runtime."""
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Lore Bard runtime covers levels 1 through 20.")
        profile = build_lyra_silverstring_2014_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        charisma_modifier = scores.modifier("charisma")
        spell_attack = pb + charisma_modifier
        armor = get_armor("leather")
        armor_class = compile_worn_armor_class(
            armor.base_ac,
            armor.category,
            scores.modifier("dexterity"),
            [],
            wielding_shield=False,
            shield_trained=False,
        )
        jack_bonus = pb // 2 if level >= 2 else 0
        healing = [
            healing_word_2014(charisma_modifier, 0),
            cure_wounds_2014(charisma_modifier, 0),
        ]
        return CombatantTemplate(
            id=profile.template_id,
            name=profile.character_name,
            archetype="Bard",
            level=level,
            kind="character",
            ruleset="2014",
            ability_scores=scores,
            armor_class=armor_class,
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=30,
            initiative_bonus=scores.modifier("dexterity") + jack_bonus,
            weapon_attack=_attack(level, scores),
            healing_actions=healing,
            persistent_spell_attack_actions=(
                [spiritual_weapon_2014(spell_attack, charisma_modifier)] if level >= 6 else []
            ),
            defensive_spell_actions=[
                *([bless_2014()] if level >= 6 else []),
                *([freedom_of_movement_2014()] if level >= 7 else []),
            ],
            condition_removal_actions=(
                [lesser_restoration_2014()] if level >= 4 else []
            ),
            effect_removal_actions=(
                [dispel_magic_2014()] if level >= 5 else []
            ),
            d20_bonus_die_actions=[build_bardic_inspiration_2014(level)],
            initiative_resource_refill_grants=build_bard_2014_initiative_refills(level),
            reaction_roll_penalty_actions=(
                [cutting_words_2014(level)] if level >= 3 else []
            ),
            timed_self_buff_actions=(
                [countercharm_2014()] if level >= 6 else []
            ),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("dexterity", "charisma")),
            skill_bonuses={
                "acrobatics": scores.modifier("dexterity") + pb * (2 if level >= 10 else 1),
                "perception": scores.modifier("wisdom") + pb * (2 if level >= 10 else 1),
                "performance": charisma_modifier + pb * (2 if level >= 3 else 1),
                "persuasion": charisma_modifier + pb * (2 if level >= 3 else 1),
            },
            weapon_masteries=[],
            resources=_resources(level, charisma_modifier),
            visual=VisualLoadout(
                armor=armor.id,
                main_hand="rapier",
                off_hand="lute",
                body_style="humanoid",
            ),
            source=(
                "D&D Basic Rules 2014: Half-Elf, Entertainer, Bard, College of Lore, "
                "Bardic Inspiration, Healing Word, Cure Wounds, Equipment"
            ),
        )
    except Exception:
        logger.exception("Failed to compile 2014 Lyra Silverstring at level %s.", level)
        raise

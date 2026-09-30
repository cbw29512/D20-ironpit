from __future__ import annotations

import logging

from app.content.cleric_life_domain import AID, DISPEL_MAGIC, LESSER_RESTORATION
from app.content.druid_2024_land_spells import (
    build_blight_2024,
    build_blur_2024,
    build_burning_hands_2024,
    build_fire_bolt_2024,
    build_lands_aid_2024,
)
from app.content.druid_2024_spells import (
    build_faerie_fire_2024,
    build_longstrider_2024,
    build_poison_spray_2024,
    build_starry_wisp_2024,
)
from app.content.healing_spell_effects import build_cure_wounds, build_healing_word
from app.content.offensive_spell_effects import build_fireball_2024
from app.content.druid_2024_wild_resurgence import build_wild_resurgence_2024
from app.content.druid_combat_levels import DRUID_COMBAT_LEVELS
from app.domain.alternate_spell_casts import AlternateSpellCastGrant
from app.domain.models import ResourceDefinition
from app.domain.replacement_form_actions import ReplacementFormAction

logger = logging.getLogger(__name__)


def wild_shape_actions(level: int) -> list[ReplacementFormAction]:
    try:
        if level < 2:
            return []
        return [ReplacementFormAction(
            id="wild-shape", name="Wild Shape", action_cost="bonus_action",
            form_template_id="srd-wolf", resource_id="wild-shape", resource_cost=1,
            voluntary_revert_action="bonus_action", hp_mode="retain_owner",
            temporary_hp_on_enter=level, retain_creature_type=True,
            ends_on_incapacitated=True, replace_existing_form=True,
            retain_spellcasting=False, source="D&D Beyond Basic Rules 2024: Druid — Wild Shape",
        )]
    except Exception:
        logger.exception("Failed to build 2024 Wild Shape at Druid level %s.", level)
        raise


def druid_resources(level: int, spell_slots: tuple[int, ...], wild_shape_uses: int) -> list[ResourceDefinition]:
    try:
        resources = [
            ResourceDefinition(
                id=f"spell-slot-{slot_level}",
                name=f"Spell Slot {slot_level}",
                max_uses=max_uses,
            )
            for slot_level, max_uses in enumerate(spell_slots, start=1)
            if max_uses
        ]
        if wild_shape_uses:
            resources.append(ResourceDefinition(
                id="wild-shape", name="Wild Shape", max_uses=wild_shape_uses,
            ))
        if level >= 5:
            resources.append(ResourceDefinition(
                id="wild-resurgence-slot-restore",
                name="Wild Resurgence: Regain Spell Slot",
                max_uses=1,
            ))
        if level >= 6:
            resources.append(ResourceDefinition(
                id="natural-recovery-free-cast",
                name="Natural Recovery: Free Circle Spell",
                max_uses=1,
            ))
        return resources
    except Exception:
        logger.exception("Failed to compile 2024 Druid resources.")
        raise


def druid_actions(level: int, proficiency_bonus: int, wisdom_modifier: int) -> dict[str, list[object]]:
    try:
        save_dc = 8 + proficiency_bonus + wisdom_modifier
        attack_bonus = proficiency_bonus + wisdom_modifier
        cantrip_damage_bonus = wisdom_modifier if level >= 7 else 0
        return {
            "saving_throw_actions": [build_lands_aid_2024(save_dc, level)] if level >= 3 else [],
            "spell_attack_actions": [
                build_poison_spray_2024(attack_bonus, level, cantrip_damage_bonus),
                *([build_fire_bolt_2024(attack_bonus, level, cantrip_damage_bonus)] if level >= 3 else []),
                *([build_starry_wisp_2024(attack_bonus, level, cantrip_damage_bonus)] if level >= 4 else []),
            ],
            "spell_save_actions": [
                *([build_faerie_fire_2024(save_dc)] if level >= 2 else []),
                *([build_burning_hands_2024(save_dc)] if level >= 3 else []),
                *([build_fireball_2024(save_dc)] if level >= 5 else []),
                *([build_blight_2024(save_dc)] if level >= 7 else []),
            ],
            "defensive_spell_actions": [
                build_longstrider_2024(),
                *([build_blur_2024()] if level >= 3 else []),
                *([AID.model_copy(deep=True)] if level >= 6 else []),
            ],
            "healing_actions": [
                build_healing_word(wisdom_modifier),
                build_cure_wounds(wisdom_modifier),
            ],
            "condition_removal_actions": [LESSER_RESTORATION] if level >= 3 else [],
            "effect_removal_actions": [DISPEL_MAGIC.model_copy(deep=True)] if level >= 5 else [],
            "resource_conversion_actions": (
                build_wild_resurgence_2024(tuple(DRUID_COMBAT_LEVELS[level].spell_slots))
                if level >= 5 else []
            ),
        }
    except Exception:
        logger.exception("Failed to compile 2024 Druid actions at level %s.", level)
        raise


def natural_recovery_alternate_casts(level: int) -> list[AlternateSpellCastGrant]:
    """Bind the 2024 Circle of the Land free Circle Spell cast to the shared alternate-cast engine."""
    try:
        if level < 6:
            return []
        return [
            AlternateSpellCastGrant(
                source_id=f"natural-recovery-{spell_id}",
                source_name="Natural Recovery",
                spell_id=spell_id,
                cast_level=cast_level,
                resource_id="natural-recovery-free-cast",
                priority=95,
            )
            for spell_id, cast_level in (
                ("burning-hands", 1),
                ("blur", 2),
                ("fireball", 3),
                *((("blight", 4),) if level >= 7 else ()),
            )
        ]
    except Exception:
        logger.exception("Failed to build 2024 Natural Recovery alternate casts at Druid level %s.", level)
        raise

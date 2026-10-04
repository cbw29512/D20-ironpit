from __future__ import annotations

import logging

from app.content.bard_2024_spells import build_greater_invisibility_2024
from app.content.sorcerer_2024_font import font_of_magic_2024_actions
from app.content.sorcerer_2024_metamagic import distant_spell_2024, heightened_spell_2024
from app.content.sorcerer_2024_spells import dragons_breath_cast_2024, magic_missile_2024
from app.content.sorcerer_combat_levels import SORCERER_COMBAT_LEVELS
from app.content.sorcerer_draconic_2024_bound_spells import (
    build_nyra_2024_spell_attacks,
    build_nyra_2024_spell_saves,
)
from app.content.sorcerer_draconic_2024_features import (
    dragon_wings_2024,
    dragon_wings_restore_2024,
    innate_sorcery_2024,
    innate_sorcery_incarnate_2024,
)
from app.domain.effect_removal import EffectRemovalAction
from app.domain.initiative_resources import InitiativeResourceRefillGrant
from app.domain.models import DamageType, ResourceDefinition
from app.domain.resource_conversion import ResourceConversionAction

logger = logging.getLogger(__name__)


def build_nyra_2024_resources(level: int):
    try:
        row = SORCERER_COMBAT_LEVELS[level]
        resources = [
            ResourceDefinition(id=f"spell-slot-{spell_level}", name=f"Spell Slot {spell_level}", max_uses=uses)
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        ]
        resources.append(ResourceDefinition(id="innate-sorcery", name="Innate Sorcery", max_uses=2))
        if level >= 2:
            resources.append(ResourceDefinition(id="sorcery-points", name="Sorcery Points", max_uses=row.sorcery_points))
        if level >= 14:
            resources.append(ResourceDefinition(id="dragon-wings", name="Dragon Wings", max_uses=1))
        if level >= 19:
            resources.append(ResourceDefinition(id="boon-of-fate", name="Boon of Fate", max_uses=1))
        return resources
    except Exception:
        logger.exception("Failed to build 2024 Nyra resources at level %s.", level)
        raise


def build_nyra_2024_conversions(level: int) -> list[ResourceConversionAction]:
    try:
        actions = font_of_magic_2024_actions(level) if level >= 2 else []
        if level >= 14:
            actions.append(dragon_wings_restore_2024())
        return actions
    except Exception:
        logger.exception("Failed to build 2024 Nyra conversions at level %s.", level)
        raise


def build_nyra_2024_self_buffs(level: int):
    try:
        buffs = [innate_sorcery_2024()]
        if level >= 3:
            buffs.append(dragons_breath_cast_2024())
        if level >= 7:
            buffs.append(innate_sorcery_incarnate_2024())
        if level >= 14:
            buffs.append(dragon_wings_2024())
        return buffs
    except Exception:
        logger.exception("Failed to build 2024 Nyra self-buffs at level %s.", level)
        raise


def build_nyra_2024_dispel() -> EffectRemovalAction:
    try:
        return EffectRemovalAction(
            id="dispel-magic",
            name="Dispel Magic",
            level=3,
            action_cost="action",
            range_ft=120,
            casting_ability="charisma",
            target_mode="enemy",
            auto_remove_max_level=3,
            resource_id="spell-slot-3",
            resource_cost=1,
            expends_spell_slot=True,
            animation="dispel-magic",
        )
    except Exception:
        logger.exception("Failed to build 2024 Sorcerer Dispel Magic.")
        raise


def build_nyra_2024_initiative_refills(level: int) -> list[InitiativeResourceRefillGrant]:
    try:
        if level < 19:
            return []
        return [InitiativeResourceRefillGrant(
            source_id="boon-of-fate",
            source_name="Boon of Fate",
            resource_id="boon-of-fate",
            when_at_or_below=0,
            restore_to_max=True,
        )]
    except Exception:
        logger.exception("Failed to build 2024 Nyra initiative refills at level %s.", level)
        raise


def build_nyra_2024_heightened(level: int):
    try:
        return [heightened_spell_2024(waive_while_innate=level >= 20)] if level >= 2 else []
    except Exception:
        logger.exception("Failed to build 2024 Nyra Heightened Spell at level %s.", level)
        raise


def build_nyra_2024_distant(level: int):
    try:
        return [distant_spell_2024()] if level >= 10 else []
    except Exception:
        logger.exception("Failed to build 2024 Nyra Distant Spell at level %s.", level)
        raise


def build_nyra_2024_defenses(level: int):
    try:
        return [build_greater_invisibility_2024()] if level >= 8 else []
    except Exception:
        logger.exception("Failed to build 2024 Nyra defenses at level %s.", level)
        raise


def build_nyra_2024_auto_hits():
    try:
        return [magic_missile_2024()]
    except Exception:
        logger.exception("Failed to build 2024 Nyra auto-hit spells.")
        raise


def nyra_2024_resistances(level: int):
    try:
        return [DamageType.FIRE] if level >= 6 else []
    except Exception:
        logger.exception("Failed to resolve 2024 Elemental Affinity resistances at level %s.", level)
        raise

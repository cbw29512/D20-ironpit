from __future__ import annotations

import logging

from app.content.bard_2024_font_of_inspiration import build_font_of_inspiration_2024
from app.content.bard_combat_levels import BARD_COMBAT_LEVELS
from app.content.bard_2024_spells import build_greater_invisibility_2024, build_shatter_2024
from app.content.cleric_life_domain import DISPEL_MAGIC
from app.content.offensive_spell_effects import build_disintegrate_2024, build_fireball_2024, build_guiding_bolt
from app.content.spell_effects import BLESS
from app.domain.combatants import ResourceDefinition
from app.domain.progression import ProgressionCombatFeatures
from app.domain.progression_primitives import FailedSaveRerollGrant

logger = logging.getLogger(__name__)


def bard_resource_conversions(level: int):
    try:
        return build_font_of_inspiration_2024(level) if level >= 5 else []
    except Exception:
        logger.exception("Failed to build 2024 Bard resource conversions at level %s.", level)
        raise


def bard_spell_attacks(level: int, spell_attack_bonus: int):
    try:
        return [build_guiding_bolt(spell_attack_bonus)] if level >= 6 else []
    except Exception:
        logger.exception("Failed to build 2024 Bard spell attacks at level %s.", level)
        raise


def bard_spell_saves(level: int, save_dc: int):
    try:
        actions = [build_shatter_2024(save_dc)] if level >= 3 else []
        if level >= 10:
            actions.append(build_fireball_2024(save_dc))
        if level >= 11:
            actions.append(build_disintegrate_2024(save_dc))
        return actions
    except Exception:
        logger.exception("Failed to build 2024 Bard spell-save actions at level %s.", level)
        raise


def bard_defensive_spells(level: int):
    try:
        if level < 6:
            return []
        return [
            BLESS.model_copy(deep=True),
            *([build_greater_invisibility_2024()] if level >= 7 else []),
        ]
    except Exception:
        logger.exception("Failed to build 2024 Bard defensive spells at level %s.", level)
        raise


def bard_effect_removals(level: int):
    try:
        return (
            [DISPEL_MAGIC.model_copy(deep=True, update={"casting_ability": "charisma"})]
            if level >= 6 else []
        )
    except Exception:
        logger.exception("Failed to build 2024 Bard effect-removal actions at level %s.", level)
        raise


def bard_progression_features(level: int) -> ProgressionCombatFeatures:
    try:
        return ProgressionCombatFeatures(
            failed_save_reroll_grants=(
                [
                    FailedSaveRerollGrant(
                        source_id="countercharm",
                        source_name="Countercharm",
                        action_cost="reaction",
                        target_mode="self_or_ally",
                        range_ft=30,
                        required_effect_tags=["charmed", "frightened"],
                        reroll_mode="advantage",
                    )
                ]
                if level >= 7 else []
            ),
        )
    except Exception:
        logger.exception("Failed to build 2024 Bard progression features at level %s.", level)
        raise


def bard_resources(level: int, charisma_modifier: int) -> list[ResourceDefinition]:
    try:
        row = BARD_COMBAT_LEVELS[level]
        resources = [
            ResourceDefinition(
                id="bardic-inspiration",
                name="Bardic Inspiration",
                max_uses=max(1, charisma_modifier),
            ),
            ResourceDefinition(
                id="adrenaline-rush",
                name="Adrenaline Rush",
                max_uses=row.proficiency_bonus,
            ),
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
        logger.exception("Failed to build 2024 Bard resources at level %s.", level)
        raise

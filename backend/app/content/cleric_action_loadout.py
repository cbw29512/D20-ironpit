from __future__ import annotations

import logging

from app.content.cleric_divine_intervention import (
    build_divine_intervention_damage,
    build_divine_intervention_healing,
)
from app.content.cleric_life_domain import AID, disciple_of_life_bonus
from app.content.healing_spell_effects import (
    build_cure_wounds,
    build_healing_word,
    build_mass_cure_wounds,
    build_mass_healing_word,
)
from app.content.offensive_spell_effects import build_inflict_wounds, build_sacred_flame
from app.content.spell_effects import BLESS, SHIELD_OF_FAITH
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def build_healing_actions(level: int, wisdom_modifier: int, features: tuple[str, ...]):
    try:
        life = "disciple-of-life" in features
        actions = [build_cure_wounds(
            wisdom_modifier,
            disciple_of_life_bonus(1) if life else 0,
        )]
        if level >= 2:
            actions.append(build_healing_word(
                wisdom_modifier,
                disciple_of_life_bonus(1) if life else 0,
            ))
        if level >= 5:
            actions.append(build_mass_healing_word(
                wisdom_modifier,
                disciple_of_life_bonus(3) if life else 0,
            ))
        if level >= 9:
            actions.append(build_mass_cure_wounds(
                wisdom_modifier,
                disciple_of_life_bonus(5) if life else 0,
            ))
        if level >= 11:
            actions.append(build_mass_cure_wounds(
                wisdom_modifier,
                disciple_of_life_bonus(6) if life else 0,
                6,
            ))
        if level >= 10:
            actions.append(build_divine_intervention_healing(
                wisdom_modifier,
                disciple_of_life_bonus(5) if life else 0,
            ))
        return actions
    except Exception:
        logger.exception("Failed to build Cleric healing actions at level %s.", level)
        raise


def build_defensive_spells(level: int):
    try:
        actions = [BLESS.model_copy(deep=True), SHIELD_OF_FAITH.model_copy(deep=True)]
        if level >= 3:
            actions.insert(0, AID.model_copy(deep=True))
        return actions
    except Exception:
        logger.exception("Failed to build Cleric defensive spells at level %s.", level)
        raise


def build_save_spells(
    level: int,
    save_dc: int,
    wisdom_modifier: int,
    features: tuple[str, ...],
):
    try:
        actions = [build_sacred_flame(
            save_dc,
            level,
            wisdom_modifier if "blessed-strikes" in features else 0,
        )]
        if level >= 4:
            actions.append(build_inflict_wounds(save_dc))
        if level >= 9:
            actions.append(build_inflict_wounds(save_dc, 5))
        if level >= 11:
            actions.append(build_inflict_wounds(save_dc, 6))
        return actions
    except Exception:
        logger.exception("Failed to build Cleric save spells at level %s.", level)
        raise


def build_divine_intervention_actions(level: int, save_dc: int):
    try:
        return [build_divine_intervention_damage(save_dc)] if level >= 10 else []
    except Exception:
        logger.exception("Failed to build Cleric Divine Intervention actions at level %s.", level)
        raise


def build_combat_traits(features: tuple[str, ...]) -> list[CombatTrait]:
    try:
        traits = [CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE]
        if "disciple-of-life" in features:
            traits.append(CombatTrait.LIFE_DOMAIN)
        return traits
    except Exception:
        logger.exception("Failed to build Cleric combat traits.")
        raise

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.shared_damage_spells_2014 import flame_strike_2014
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
from app.content.shared_healing_spells_2014 import heal_2014, mass_healing_word_2014
from app.content.shared_movement_spells_2014 import freedom_of_movement_2014
from app.content.shared_restoration_spells_2014 import greater_restoration_2014
from app.domain.actions import ConditionRemovalAction, HealingAction
from app.domain.effect_removal import EffectRemovalAction
from app.domain.spells import DefensiveSpellAction, SpellSaveAction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClericLife2014BoundSpells:
    healing: tuple[HealingAction, ...]
    defenses: tuple[DefensiveSpellAction, ...]
    saves: tuple[SpellSaveAction, ...]
    effect_removals: tuple[EffectRemovalAction, ...]
    condition_removals: tuple[ConditionRemovalAction, ...]


def bind_cleric_life_2014_prepared_spells(
    level: int,
    wisdom_modifier: int,
    save_dc: int,
) -> ClericLife2014BoundSpells:
    """Bind prepared 2014 Life Cleric spells that existing primitives can represent."""
    try:
        package = build_cleric_2014_spell_package(level, wisdom_modifier)
        prepared = {spell.id for spell in (*package.spells, *package.always_prepared_spells)}
        healing: list[HealingAction] = []
        if "mass-healing-word" in prepared:
            healing.append(mass_healing_word_2014(wisdom_modifier, additional_healing_bonus=5))
        if "heal" in prepared:
            healing.append(heal_2014(additional_healing_bonus=8))
        return ClericLife2014BoundSpells(
            healing=tuple(healing),
            defenses=(
                (freedom_of_movement_2014(),)
                if "freedom-of-movement" in prepared else ()
            ),
            saves=((flame_strike_2014(save_dc),) if "flame-strike" in prepared else ()),
            effect_removals=(
                (dispel_magic_2014("wisdom"),)
                if "dispel-magic" in prepared else ()
            ),
            condition_removals=(
                (greater_restoration_2014(),)
                if "greater-restoration" in prepared else ()
            ),
        )
    except Exception:
        logger.exception("Failed to bind prepared 2014 Life Cleric spells at level %s.", level)
        raise

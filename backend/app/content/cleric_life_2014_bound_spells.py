from __future__ import annotations

import logging
from dataclasses import dataclass

from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.shared_control_spells_2014 import (
    hold_person_2014,
    silence_2014,
    spirit_guardians_2014,
)
from app.content.shared_damage_spells_2014 import flame_strike_2014, harm_2014
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
from app.content.shared_healing_spells_2014 import heal_2014, mass_healing_word_2014
from app.content.shared_movement_spells_2014 import freedom_of_movement_2014
from app.content.shared_restoration_spells_2014 import greater_restoration_2014, remove_curse_2014
from app.content.shared_ward_spells_2014 import protection_from_energy_2014, warding_bond_2014
from app.domain.actions import ConditionRemovalAction, HealingAction
from app.domain.effect_removal import EffectRemovalAction
from app.domain.spells import DefensiveSpellAction, SpellSaveAction
from app.domain.suppression_zones import PersistentSuppressionZoneAction
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClericLife2014BoundSpells:
    healing: tuple[HealingAction, ...]
    defenses: tuple[DefensiveSpellAction, ...]
    saves: tuple[SpellSaveAction, ...]
    effect_removals: tuple[EffectRemovalAction, ...]
    condition_removals: tuple[ConditionRemovalAction, ...]
    timed_self_buffs: tuple[TimedSelfBuffAction, ...]
    suppression_zones: tuple[PersistentSuppressionZoneAction, ...]


def bind_cleric_life_2014_prepared_spells(
    level: int,
    wisdom_modifier: int,
    save_dc: int,
) -> ClericLife2014BoundSpells:
    """Bind prepared 2014 Life Cleric spells that the universal engine can resolve."""
    try:
        package = build_cleric_2014_spell_package(level, wisdom_modifier)
        prepared = {spell.id for spell in (*package.spells, *package.always_prepared_spells)}
        healing: list[HealingAction] = []
        if "mass-healing-word" in prepared:
            healing.append(mass_healing_word_2014(wisdom_modifier, additional_healing_bonus=5))
        if "heal" in prepared:
            healing.append(heal_2014(additional_healing_bonus=8))
        defenses: list[DefensiveSpellAction] = []
        if "freedom-of-movement" in prepared:
            defenses.append(freedom_of_movement_2014())
        if "warding-bond" in prepared:
            defenses.append(warding_bond_2014())
        if "protection-from-energy" in prepared:
            defenses.append(protection_from_energy_2014())
        saves: list[SpellSaveAction] = []
        if "hold-person" in prepared:
            saves.append(hold_person_2014(save_dc))
        if "flame-strike" in prepared:
            saves.append(flame_strike_2014(save_dc))
        if "harm" in prepared:
            saves.append(harm_2014(save_dc))
        removals: list[ConditionRemovalAction] = []
        if "remove-curse" in prepared:
            removals.append(remove_curse_2014())
        if "greater-restoration" in prepared:
            removals.append(greater_restoration_2014())
        return ClericLife2014BoundSpells(
            healing=tuple(healing),
            defenses=tuple(defenses),
            saves=tuple(saves),
            effect_removals=(
                (dispel_magic_2014("wisdom"),)
                if "dispel-magic" in prepared else ()
            ),
            condition_removals=tuple(removals),
            timed_self_buffs=(
                (spirit_guardians_2014(save_dc),)
                if "spirit-guardians" in prepared else ()
            ),
            suppression_zones=((silence_2014(),) if "silence" in prepared else ()),
        )
    except Exception:
        logger.exception("Failed to bind prepared 2014 Life Cleric spells at level %s.", level)
        raise

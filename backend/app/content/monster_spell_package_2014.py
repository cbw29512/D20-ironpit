from __future__ import annotations

from dataclasses import dataclass
import logging

from app.content.monster_healing_2014 import healing_actions_2014
from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.monster_innate_support_2014 import (
    innate_alternate_spell_casts_2014,
    innate_condition_removal_2014,
    innate_spell_names_2014,
    innate_spell_resources_2014,
    innate_timed_self_buffs_2014,
    supports_innate_spellcasting_2014,
)
from app.content.monster_slot_spells_2014 import (
    slot_defensive_spells_2014,
    slot_healing_actions_2014,
    slot_spell_names_2014,
    slot_spell_resources_2014,
    slot_spell_save_actions_2014,
    supports_slot_spellcasting_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.domain.actions import ConditionRemovalAction, HealingAction
from app.domain.alternate_spell_casts import AlternateSpellCastGrant
from app.domain.combatants import ResourceDefinition
from app.domain.spells import DefensiveSpellAction, SpellSaveAction
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MonsterSpellPackage2014:
    spell_save_actions: list[SpellSaveAction]
    defensive_spell_actions: list[DefensiveSpellAction]
    healing_actions: list[HealingAction]
    timed_self_buff_actions: list[TimedSelfBuffAction]
    condition_removal_actions: list[ConditionRemovalAction]
    resources: list[ResourceDefinition]
    alternate_spell_cast_grants: list[AlternateSpellCastGrant]


def supports_monster_spellcasting_2014(monster: SourceMonster2014) -> bool:
    """True when every printed innate/slot spell is bound, arena-neutral, or pit-banned."""
    try:
        if monster.spellcasting and monster.innate_spellcasting:
            return False
        if monster.spellcasting:
            return supports_slot_spellcasting_2014(monster)
        return supports_innate_spellcasting_2014(monster)
    except Exception:
        logger.exception("Failed to classify 2014 monster spellcasting for %s.", monster.name)
        raise


def bound_spell_action_names_2014(monster: SourceMonster2014) -> set[str]:
    return innate_spell_names_2014(monster) | slot_spell_names_2014(monster)


def bound_spell_resource_ids_2014(monster: SourceMonster2014) -> set[str]:
    return {item.id for item in innate_spell_resources_2014(monster)} | {
        item.id for item in slot_spell_resources_2014(monster)
    }


def spell_package_2014(monster: SourceMonster2014) -> MonsterSpellPackage2014:
    """Compose innate and slot spell fields for the 2014 adapter."""
    try:
        return MonsterSpellPackage2014(
            spell_save_actions=[
                *innate_spell_save_actions_2014(monster),
                *slot_spell_save_actions_2014(monster),
            ],
            defensive_spell_actions=slot_defensive_spells_2014(monster),
            healing_actions=[
                *healing_actions_2014(monster),
                *slot_healing_actions_2014(monster),
            ],
            timed_self_buff_actions=innate_timed_self_buffs_2014(monster),
            condition_removal_actions=innate_condition_removal_2014(monster),
            resources=[
                *innate_spell_resources_2014(monster),
                *slot_spell_resources_2014(monster),
            ],
            alternate_spell_cast_grants=innate_alternate_spell_casts_2014(monster),
        )
    except Exception:
        logger.exception("Failed to compose the 2014 spell package for %s.", monster.name)
        raise

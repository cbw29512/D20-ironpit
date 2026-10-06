from __future__ import annotations

import logging

from app.content.monster_innate_spells_2014 import (
    ARENA_NEUTRAL_INNATE_SPELLS_2014,
    _PIT_BANNED_INNATE_SPELLS_2014,
    _DISPEL_ATTACKER_TYPES_2014,
    _innate,
    _spells,
    innate_spell_save_actions_2014,
)
from app.domain.actions import ConditionRemovalAction
from app.domain.alternate_spell_casts import AlternateSpellCastGrant
from app.domain.combatants import ResourceDefinition
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def innate_timed_self_buffs_2014(monster) -> list[TimedSelfBuffAction]:
    """Bind in-combat innate self-buffs. Dismissal/plane-shift functions stay omitted."""
    try:
        actions: list[TimedSelfBuffAction] = []
        for spell in _spells(monster):
            if str(spell.get("id") or "") != "dispel-evil-and-good":
                continue
            actions.append(TimedSelfBuffAction(
                id="dispel-evil-and-good",
                name="Dispel Evil and Good",
                action_cost="action",
                resource_id="dispel-evil-and-good",
                resource_cost=1,
                duration_rounds=10,
                expiry_timing="source_turn_end",
                concentration=True,
                modifier_effects=[
                    SpellModifierEffect(
                        kind="attacks-against-disadvantage",
                        source_creature_types=list(_DISPEL_ATTACKER_TYPES_2014),
                    )
                ],
                animation="dispel-evil-and-good",
            ))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 innate timed self-buffs for %s.", monster.name)
        raise


def innate_condition_removal_2014(monster) -> list[ConditionRemovalAction]:
    """Bind Dispel Evil and Good's Break Enchantment; omit Dismissal (plane shift)."""
    try:
        if not any(str(spell.get("id") or "") == "dispel-evil-and-good" for spell in _spells(monster)):
            return []
        return [ConditionRemovalAction(
            id="break-enchantment",
            name="Break Enchantment",
            action_cost="action",
            range_ft=5,
            target_mode="self_or_ally",
            removable_conditions=["charmed", "frightened"],
            requires_active_effect_id="dispel-evil-and-good",
            ends_required_effect=True,
            animation="break-enchantment",
        )]
    except Exception:
        logger.exception("Failed to compile 2014 innate condition removal for %s.", monster.name)
        raise


def innate_spell_resources_2014(monster) -> list[ResourceDefinition]:
    try:
        resources: list[ResourceDefinition] = []
        bound = {action.id for action in innate_spell_save_actions_2014(monster)}
        bound.update(action.id for action in innate_timed_self_buffs_2014(monster))
        for spell in _spells(monster):
            spell_id = str(spell.get("id") or "")
            if spell_id not in bound or str(spell.get("usage") or "") != "per_day":
                continue
            uses = int(spell.get("uses_per_day") or 0)
            if uses <= 0:
                raise ValueError(f"{monster.name} innate spell {spell_id} lacks a daily use count.")
            resources.append(ResourceDefinition(
                id=spell_id,
                name=str(spell.get("name") or spell_id).replace("-", " ").title(),
                max_uses=uses,
            ))
        return resources
    except Exception:
        logger.exception("Failed to compile 2014 innate spell resources for %s.", monster.name)
        raise


def innate_alternate_spell_casts_2014(monster) -> list[AlternateSpellCastGrant]:
    """Spend printed 1/day innate uses instead of hero spell slots."""
    try:
        resources = {item.id for item in innate_spell_resources_2014(monster)}
        return [
            AlternateSpellCastGrant(
                source_id=action.id, source_name=action.name, spell_id=action.id,
                cast_level=max(1, action.level), resource_id=action.id, resource_cost=1,
            )
            for action in innate_spell_save_actions_2014(monster) if action.id in resources
        ]
    except Exception:
        logger.exception("Failed to compile 2014 innate alternate casts for %s.", monster.name)
        raise


def innate_spell_names_2014(monster) -> set[str]:
    from app.content.monster_charm_control import charm_control_spell_actions_2014
    names = {action.name.casefold() for action in innate_spell_save_actions_2014(monster)}
    names.update(action.name.casefold() for action in innate_timed_self_buffs_2014(monster))
    names.update(action.name.casefold() for action in innate_condition_removal_2014(monster))
    names.update(action.name.casefold() for action in charm_control_spell_actions_2014(monster))
    return names


def supports_innate_spellcasting_2014(monster) -> bool:
    try:
        if monster.spellcasting:
            return False
        if _innate(monster) is None:
            return True
        if not _innate(monster).get("source_complete"):
            return False
        known = {str(spell.get("id") or "") for spell in _spells(monster)}
        if not known:
            return False
        from app.content.monster_charm_control import CHARM_CONTROL_SPELL_IDS
        bound = ARENA_NEUTRAL_INNATE_SPELLS_2014 | _PIT_BANNED_INNATE_SPELLS_2014 | CHARM_CONTROL_SPELL_IDS | {
            action.id for action in innate_spell_save_actions_2014(monster)
        } | {
            action.id for action in innate_timed_self_buffs_2014(monster)
        }
        return known <= bound
    except Exception:
        logger.exception("Failed to classify 2014 innate spellcasting for %s.", monster.name)
        raise

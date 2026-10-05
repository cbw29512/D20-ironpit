from __future__ import annotations

import logging

from app.content.cleric_2014_level1_spells import bless_2014, cure_wounds_2014, sacred_flame_2014
from app.content.monster_innate_spells_2014 import (
    ARENA_NEUTRAL_INNATE_SPELLS_2014,
    _PIT_BANNED_INNATE_SPELLS_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.shared_spells_2014 import sanctuary_2014
from app.domain.actions import HealingAction
from app.domain.combatants import ResourceDefinition
from app.domain.spells import DefensiveSpellAction, SpellSaveAction

logger = logging.getLogger(__name__)
_ABILITY_KEYS = {
    "str": "strength",
    "dex": "dexterity",
    "con": "constitution",
    "int": "intelligence",
    "wis": "wisdom",
    "cha": "charisma",
}


def _slots(monster: SourceMonster2014) -> dict[str, object] | None:
    raw = monster.spellcasting
    return raw if isinstance(raw, dict) else None


def _spells(monster: SourceMonster2014) -> list[dict[str, object]]:
    data = _slots(monster)
    if data is None:
        return []
    spells = data.get("spells") or []
    if not isinstance(spells, list):
        raise ValueError(f"{monster.name} spell list is not structured.")
    return [item for item in spells if isinstance(item, dict)]


def _known_ids(monster: SourceMonster2014) -> set[str]:
    return {str(spell.get("id") or "") for spell in _spells(monster)} - {""}


def _dc(monster: SourceMonster2014) -> int | None:
    data = _slots(monster)
    if data is None:
        return None
    raw = data.get("save_dc")
    return int(raw) if raw is not None else None


def _caster_level(monster: SourceMonster2014) -> int:
    data = _slots(monster)
    if data is None:
        return 1
    return max(1, int(data.get("caster_level") or 1))


def _ability_modifier(monster: SourceMonster2014) -> int:
    data = _slots(monster) or {}
    ability = str(data.get("ability") or "wisdom")
    full = _ABILITY_KEYS.get(ability, ability)
    score = monster.abilities.get(ability)
    if score is None:
        short = next((key for key, name in _ABILITY_KEYS.items() if name == full), None)
        score = monster.abilities.get(short) if short else None
    if score is None:
        raise ValueError(f"{monster.name} is missing {full} for slot spellcasting.")
    return (int(score) - 10) // 2


def slot_spell_save_actions_2014(monster: SourceMonster2014) -> list[SpellSaveAction]:
    """Bind printed slot save spells through existing hero constructors."""
    try:
        dc = _dc(monster)
        if dc is None or "sacred-flame" not in _known_ids(monster):
            return []
        return [sacred_flame_2014(dc, _caster_level(monster))]
    except Exception:
        logger.exception("Failed to compile 2014 slot save spells for %s.", monster.name)
        raise


def slot_defensive_spells_2014(monster: SourceMonster2014) -> list[DefensiveSpellAction]:
    """Bind printed slot buffs through existing hero constructors."""
    try:
        known = _known_ids(monster)
        dc = _dc(monster)
        actions: list[DefensiveSpellAction] = []
        if "bless" in known:
            actions.append(bless_2014())
        if "sanctuary" in known and dc is not None:
            actions.append(sanctuary_2014(dc))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 slot defensive spells for %s.", monster.name)
        raise


def slot_healing_actions_2014(monster: SourceMonster2014) -> list[HealingAction]:
    """Bind Cure Wounds with the printed casting-ability modifier and no Life bonus."""
    try:
        if "cure-wounds" not in _known_ids(monster):
            return []
        return [cure_wounds_2014(_ability_modifier(monster), 0)]
    except Exception:
        logger.exception("Failed to compile 2014 slot healing spells for %s.", monster.name)
        raise


def slot_spell_resources_2014(monster: SourceMonster2014) -> list[ResourceDefinition]:
    try:
        data = _slots(monster)
        if data is None:
            return []
        slots = data.get("slots") or {}
        if not isinstance(slots, dict):
            raise ValueError(f"{monster.name} spell slots are not structured.")
        resources: list[ResourceDefinition] = []
        for level, uses in slots.items():
            count = int(uses)
            if count <= 0:
                raise ValueError(f"{monster.name} has invalid slot count for level {level}.")
            resources.append(ResourceDefinition(
                id=f"spell-slot-{int(level)}",
                name=f"Level {int(level)} Spell Slot",
                max_uses=count,
            ))
        return resources
    except Exception:
        logger.exception("Failed to compile 2014 slot resources for %s.", monster.name)
        raise


def slot_spell_names_2014(monster: SourceMonster2014) -> set[str]:
    names = {action.name.casefold() for action in slot_spell_save_actions_2014(monster)}
    names.update(action.name.casefold() for action in slot_defensive_spells_2014(monster))
    names.update(action.name.casefold() for action in slot_healing_actions_2014(monster))
    return names


def supports_slot_spellcasting_2014(monster: SourceMonster2014) -> bool:
    try:
        if monster.innate_spellcasting:
            return False
        data = _slots(monster)
        if data is None:
            return True
        if not data.get("source_complete"):
            return False
        known = _known_ids(monster)
        if not known:
            return False
        bound = ARENA_NEUTRAL_INNATE_SPELLS_2014 | _PIT_BANNED_INNATE_SPELLS_2014 | {
            action.id for action in slot_spell_save_actions_2014(monster)
        } | {
            action.id for action in slot_defensive_spells_2014(monster)
        } | {
            action.id for action in slot_healing_actions_2014(monster)
        }
        return known <= bound
    except Exception:
        logger.exception("Failed to classify 2014 slot spellcasting for %s.", monster.name)
        raise

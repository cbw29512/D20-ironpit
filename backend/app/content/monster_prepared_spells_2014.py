from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_tier1_cleric_2014 import source_proves_tier1_cleric_spells_2014
from app.content.monster_tier1_cleric_actions_2014 import tier1_cleric_save_spells_2014
from app.content.shared_control_spells_2014 import (
    blindness_deafness_2014,
    hold_monster_2014,
)
from app.content.shared_damage_spells_2014 import flame_strike_2014, harm_2014
from app.content.shared_zone_spells_2014 import wall_of_fire_2014
from app.content.sorcerer_draconic_2014_spells import (
    burning_hands_2014,
    cone_of_cold_2014,
    fire_bolt_2014,
    fireball_2014,
    lightning_bolt_2014,
    poison_spray_2014,
    ray_of_frost_2014,
    shatter_2014,
)
from app.content.sorcerer_draconic_2014_spell_support import magic_missile_2014, shocking_grasp_2014
from app.content.bard_2014_vicious_mockery import vicious_mockery_action_2014
from app.domain.auto_hit_spells import AutoHitSpellAction
from app.domain.persistent_save_zones import PersistentSaveZoneAction
from app.domain.spells import SpellAttackAction, SpellSaveAction

logger = logging.getLogger(__name__)

# Conservative cantrip scaling for monsters (no character level on prepared cards).
_MONSTER_CANTRIP_LEVEL = 1


def _prepared_spells(monster: SourceMonster2014) -> list[dict[str, object]]:
    source = monster.spellcasting
    if not isinstance(source, dict) or not source.get("source_complete"):
        return []
    spells = source.get("spells") or []
    return [item for item in spells if isinstance(item, dict)]


def _save_dc(monster: SourceMonster2014) -> int | None:
    source = monster.spellcasting
    if not isinstance(source, dict):
        return None
    raw = source.get("save_dc")
    return int(raw) if raw is not None else None


def _attack_bonus(monster: SourceMonster2014) -> int | None:
    source = monster.spellcasting
    if not isinstance(source, dict):
        return None
    raw = source.get("attack_bonus")
    return int(raw) if raw is not None else None


def prepared_spell_save_actions_2014(monster: SourceMonster2014) -> list[SpellSaveAction]:
    """Bind printed prepared save spells. Highest-level damage first."""
    try:
        actions: list[SpellSaveAction] = []
        dc = _save_dc(monster)
        if dc is None:
            return actions
        for spell in _prepared_spells(monster):
            spell_id = str(spell.get("id") or "")
            # Highest-level damage first
            if spell_id == "harm":
                actions.append(harm_2014(dc))
            elif spell_id == "cone-of-cold":
                actions.append(cone_of_cold_2014(dc))
            elif spell_id == "flame-strike":
                actions.append(flame_strike_2014(dc))
            elif spell_id == "lightning-bolt":
                actions.append(lightning_bolt_2014(dc))
            elif spell_id == "fireball":
                actions.append(fireball_2014(dc))
            elif spell_id == "shatter":
                actions.append(shatter_2014(dc))
            elif spell_id == "burning-hands":
                actions.append(burning_hands_2014(dc))
            elif spell_id == "poison-spray":
                actions.append(poison_spray_2014(dc, _MONSTER_CANTRIP_LEVEL))
            elif spell_id == "hold-monster":
                actions.append(hold_monster_2014(dc))
            elif spell_id == "blindness-deafness":
                actions.append(blindness_deafness_2014(dc))
            elif spell_id == "vicious-mockery":
                actions.append(vicious_mockery_action_2014(dc))
        actions.extend(tier1_cleric_save_spells_2014(monster))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 prepared save spells for %s.", monster.name)
        raise


def prepared_spell_attack_actions_2014(monster: SourceMonster2014) -> list[SpellAttackAction]:
    """Bind printed prepared attack spells (cantrips)."""
    try:
        actions: list[SpellAttackAction] = []
        attack_bonus = _attack_bonus(monster)
        if attack_bonus is None:
            return actions
        for spell in _prepared_spells(monster):
            spell_id = str(spell.get("id") or "")
            if spell_id == "fire-bolt":
                actions.append(fire_bolt_2014(int(attack_bonus), _MONSTER_CANTRIP_LEVEL))
            elif spell_id == "ray-of-frost":
                actions.append(ray_of_frost_2014(int(attack_bonus), _MONSTER_CANTRIP_LEVEL))
            elif spell_id == "shocking-grasp":
                actions.append(shocking_grasp_2014(int(attack_bonus), _MONSTER_CANTRIP_LEVEL))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 prepared attack spells for %s.", monster.name)
        raise


def prepared_auto_hit_spell_actions_2014(monster: SourceMonster2014) -> list[AutoHitSpellAction]:
    try:
        return [
            magic_missile_2014()
            for spell in _prepared_spells(monster)
            if str(spell.get("id") or "") == "magic-missile"
        ]
    except Exception:
        logger.exception("Failed to compile 2014 prepared auto-hit spells for %s.", monster.name)
        raise


def prepared_persistent_save_zone_actions_2014(
    monster: SourceMonster2014,
) -> list[PersistentSaveZoneAction]:
    try:
        dc = _save_dc(monster)
        if dc is None:
            return []
        return [
            wall_of_fire_2014(dc).model_copy(update={"resource_id": "wall-of-fire"})
            for spell in _prepared_spells(monster)
            if str(spell.get("id") or "") == "wall-of-fire"
        ]
    except Exception:
        logger.exception("Failed to compile 2014 prepared save zones for %s.", monster.name)
        raise


def supports_prepared_spellcasting_2014(monster: SourceMonster2014) -> bool:
    """True when every printed prepared spell is bound or arena-neutral."""
    try:
        if not monster.spellcasting:
            return True
        source = monster.spellcasting
        if not isinstance(source, dict) or not source.get("source_complete"):
            return False
        known = {str(spell.get("id") or "") for spell in _prepared_spells(monster)}
        if not known:
            return False
        bound = {
            action.id for action in prepared_spell_save_actions_2014(monster)
        } | {
            action.id for action in prepared_spell_attack_actions_2014(monster)
        } | {
            action.id for action in prepared_auto_hit_spell_actions_2014(monster)
        } | {
            action.id for action in prepared_persistent_save_zone_actions_2014(monster)
        }
        # Only a complete, source-proven utility clause is arena-neutral.
        # Other unrecognized spells continue blocking their entire caster.
        if source_proves_tier1_cleric_spells_2014(monster):
            bound.update({"light", "thaumaturgy", "bless", "cure-wounds", "sanctuary"})
        return known <= bound
    except Exception:
        logger.exception("Failed to classify 2014 prepared spellcasting for %s.", monster.name)
        raise

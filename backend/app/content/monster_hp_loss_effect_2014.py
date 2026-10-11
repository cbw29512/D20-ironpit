"""Strict source-to-universal binding for on-hit direct-HP-loss mechanics."""

from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceAttack2014
from app.domain.capability_effects import OngoingHpLossEffectDefinition

logger = logging.getLogger(__name__)

_ONGOING_KEYS = frozenset({
    "id", "name", "dice_count", "dice_size", "apply_on",
    "stacks_on_reapply", "ends_on_magical_healing",
    "removal_ability", "removal_skill", "removal_dc",
})
_SAVE_KEYS = frozenset({
    "save_ability", "dc", "excluded_creature_types", "gates_ongoing_damage",
})
_ABILITIES = frozenset({
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
})


def supported_ongoing_hp_loss_2014(attack: SourceAttack2014) -> bool:
    """Accept only a printed source pattern whose semantics are fully modeled."""
    try:
        wound = attack.ongoing_damage_effect
        save = attack.on_hit_save_effect
        if not isinstance(wound, dict) or not isinstance(save, dict):
            return False
        if set(wound) != _ONGOING_KEYS or set(save) != _SAVE_KEYS:
            return False
        excluded = save.get("excluded_creature_types")
        return (
            isinstance(wound["id"], str) and bool(wound["id"])
            and isinstance(wound["name"], str) and bool(wound["name"])
            and isinstance(wound["dice_count"], int) and 0 < wound["dice_count"] <= 40
            and isinstance(wound["dice_size"], int) and 2 <= wound["dice_size"] <= 100
            and wound["apply_on"] == "failed_on_hit_save"
            and wound["stacks_on_reapply"] is True
            and wound["ends_on_magical_healing"] is True
            and wound["removal_ability"] == "wisdom"
            and wound["removal_skill"] == "medicine"
            and isinstance(wound["removal_dc"], int) and wound["removal_dc"] > 0
            and str(save["save_ability"]).lower() in _ABILITIES
            and isinstance(save["dc"], int) and 0 < save["dc"] <= 40
            and save["gates_ongoing_damage"] is True
            and isinstance(excluded, list)
            and all(isinstance(item, str) and bool(item) for item in excluded)
        )
    except (KeyError, ValueError, TypeError):
        logger.exception("Malformed ongoing HP-loss source pattern for %s.", attack.id)
        return False


def ongoing_hp_loss_effect_2014(attack: SourceAttack2014) -> OngoingHpLossEffectDefinition:
    try:
        if not supported_ongoing_hp_loss_2014(attack):
            raise ValueError(f"Unsupported ongoing HP loss on {attack.id}.")
        wound = attack.ongoing_damage_effect
        save = attack.on_hit_save_effect
        return OngoingHpLossEffectDefinition(
            effect_id=wound["id"], source_name=wound["name"],
            save_ability=str(save["save_ability"]).lower(), dc=save["dc"],
            dice_count=wound["dice_count"], dice_size=wound["dice_size"],
            excluded_creature_types=list(save["excluded_creature_types"]),
            stacks_on_reapply=wound["stacks_on_reapply"],
            ends_on_magical_healing=wound["ends_on_magical_healing"],
        )
    except Exception:
        logger.exception("Failed to bind source ongoing HP loss for %s.", attack.id)
        raise

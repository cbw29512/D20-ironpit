"""Validated form boundary shared by official content and future homebrew editors.

The form is NOT another combat engine. It compiles into the existing
CombatantTemplate and all fight mutations remain in CombatantState.
"""
from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from app.content.capability_compiler import compile_combatant
from app.domain.capabilities import CombatantDefinition
from app.domain.capability_attacks import (
    AttackCapabilityDefinition, SaveCapabilityDefinition, ChargeProfileDefinition,
    ChargeDamageDefinition,
)
from app.domain.targeting import AreaTargeting
from app.domain.capability_effects import (
    ConditionEffectDefinition, ContestedMovementEffectDefinition, DamageEffectDefinition,
    GrappleEffectDefinition, OngoingHpLossEffectDefinition, ProneEffectDefinition,
    SaveConditionEffectDefinition, SaveDamageEffectDefinition,
    SaveMaximumHpReductionEffectDefinition, DiceSpec,
)
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.models import CombatantTemplate
from app.domain.combatants import ResourceDefinition
from app.domain.recharge import RechargeRule

logger = logging.getLogger(__name__)


_EFFECT_TYPES = {
    "damage": DamageEffectDefinition,
    "save_damage": SaveDamageEffectDefinition,
    "save_max_hp_reduction": SaveMaximumHpReductionEffectDefinition,
    "contested_movement": ContestedMovementEffectDefinition,
    "prone": ProneEffectDefinition,
    "ongoing_hp_loss": OngoingHpLossEffectDefinition,
    "save_condition": SaveConditionEffectDefinition,
    "grapple": GrappleEffectDefinition,
    "condition": ConditionEffectDefinition,
    "attacks-against-advantage": HitModifierEffect,
    "speed": HitModifierEffect,
}
# Other existing discriminator kinds are intentionally validated by Pydantic;
# they must not be guessed from user-visible names.


def _check_keys(values: object, model: type, context: str) -> None:
    try:
        if not isinstance(values, Mapping):
            raise ValueError(f"{context} must be an object.")
        extras = set(values) - set(model.model_fields)
        if extras:
            raise ValueError(f"{context} has unknown fields: {', '.join(sorted(map(str, extras)))}")
    except Exception:
        logger.exception("Invalid keys at %s", context)
        raise


def compile_combatant_form(values: Mapping[str, Any]) -> CombatantTemplate:
    """Validate submitted declarative fields and reuse the canonical compiler."""
    try:
        _check_keys(values, CombatantDefinition, "combatant")
        for i, attack in enumerate(values.get("attacks", [])):
            _check_keys(attack, AttackCapabilityDefinition, f"attacks[{i}]")
            if "damage" in attack and attack["damage"] is not None:
                _check_keys(attack["damage"], DiceSpec, f"attacks[{i}].damage")
            if attack.get("charge_profile") is not None:
                charge = attack["charge_profile"]
                label = f"attacks[{i}].charge_profile"
                _check_keys(charge, ChargeProfileDefinition, label)
                for component in ("bonus_damage", "replacement_damage"):
                    if charge.get(component) is not None:
                        _check_keys(charge[component], ChargeDamageDefinition, f"{label}.{component}")
            for j, effect in enumerate(attack.get("effects", [])):
                label = f"attacks[{i}].effects[{j}]"
                if not isinstance(effect, Mapping):
                    raise ValueError(f"{label} must be an object.")
                kind = effect.get("kind")
                if kind in _EFFECT_TYPES:
                    _check_keys(effect, _EFFECT_TYPES[kind], label)
                if kind in {"damage", "save_damage"} and "dice" in effect:
                    _check_keys(effect["dice"], DiceSpec, f"{label}.dice")
        for i, action in enumerate(values.get("save_actions", [])):
            label = f"save_actions[{i}]"
            _check_keys(action, SaveCapabilityDefinition, label)
            if action.get("damage") is not None:
                _check_keys(action["damage"], DiceSpec, f"{label}.damage")
            if action.get("grapple") is not None:
                _check_keys(action["grapple"], GrappleEffectDefinition, f"{label}.grapple")
            if action.get("area") is not None:
                _check_keys(action["area"], AreaTargeting, f"{label}.area")
        for i, resource in enumerate(values.get("resources", [])):
            _check_keys(resource, ResourceDefinition, f"resources[{i}]")
        for i, recharge in enumerate(values.get("recharge_rules", [])):
            _check_keys(recharge, RechargeRule, f"recharge_rules[{i}]")
        definition = CombatantDefinition.model_validate(dict(values))
        # Unsupported capabilities are still rejected by the same compiler.
        return compile_combatant(definition)
    except (ValueError, ValidationError):
        logger.exception("Invalid combatant form: %s", values.get("id", "<unknown>") if isinstance(values, Mapping) else "<invalid>")
        raise
    except Exception:
        logger.exception("Combatant form compilation failed.")
        raise

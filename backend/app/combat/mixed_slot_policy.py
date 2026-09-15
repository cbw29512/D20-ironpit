from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant
from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.save_effects import ConditionEffectDefinition, GrappleEffectDefinition, ProneEffectDefinition
from app.domain.size import size_at_most


def _size_allowed(target: EncounterCombatant, maximum) -> bool:
    return maximum is None or size_at_most(target.state.template.size, maximum)


def _condition_is_new(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    effect: ConditionEffectDefinition,
) -> bool:
    if not _size_allowed(target, effect.max_target_size):
        return False
    if condition_is_immune(target.state, effect.condition):
        return False
    if effect.condition not in target.state.active_effect_ids:
        return True
    return not any(
        timed.effect_id == effect.condition
        and timed.source_id == attacker.combatant_id
        and timed.source_effect_id == action.id
        for timed in target.state.timed_effects
    )


def _effect_is_new(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    effect,
) -> bool:
    if isinstance(effect, ProneEffectDefinition):
        return (
            _size_allowed(target, effect.max_target_size)
            and "prone" not in target.state.active_effect_ids
            and not condition_is_immune(target.state, "prone")
        )
    if isinstance(effect, GrappleEffectDefinition):
        return _size_allowed(target, effect.max_target_size) and not any(
            source.source_id == attacker.combatant_id for source in target.state.grapple_sources
        )
    if isinstance(effect, ConditionEffectDefinition):
        return _condition_is_new(attacker, target, action, effect)
    if isinstance(effect, CombatModifierEffect):
        return not any(
            modifier.source_id == attacker.combatant_id and modifier.source_effect_id == action.id
            for modifier in target.state.active_modifiers
        )
    raise ValueError(f"Unsupported mixed-slot failed-save effect: {effect!r}")


def prefer_save_replacement(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
) -> bool:
    """Prefer a mixed-slot save when failure can add a currently meaningful control effect."""
    if any(_effect_is_new(attacker, target, action, effect) for effect in action.failure_effects):
        return True
    if action.grapple_escape_dc is not None:
        return not any(source.source_id == attacker.combatant_id for source in target.state.grapple_sources)
    return False

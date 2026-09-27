from __future__ import annotations

import logging

from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant
from app.domain.spell_cast_effects import SpellCastTimedResistance
from app.domain.spells import SpellAttackAction, SpellSaveAction

logger = logging.getLogger(__name__)


def _damage_types(spell: SpellAttackAction | SpellSaveAction) -> set[str]:
    try:
        result: set[str] = set()
        if spell.damage_type is not None:
            result.add(getattr(spell.damage_type, "value", str(spell.damage_type)))
        for component in getattr(spell, "damage_components", []):
            result.add(getattr(component.damage_type, "value", str(component.damage_type)))
        return result
    except Exception as exc:
        logger.exception("Failed to inspect spell damage types for %s.", spell.id)
        raise RuntimeError("Spell damage types could not be inspected.") from exc


def apply_spell_cast_timed_resistance(
    caster: EncounterCombatant,
    spell: SpellAttackAction | SpellSaveAction,
    round_number: int,
) -> SpellCastTimedResistance | None:
    """Apply the highest-priority legal matching cast-triggered resistance option."""
    try:
        candidates = sorted(
            caster.state.template.spell_cast_timed_resistances,
            key=lambda item: item.priority,
            reverse=True,
        )
        spell_types = _damage_types(spell)
        for option in candidates:
            if option.qualifying_damage_type.value not in spell_types:
                continue
            active_resistances = {
                *caster.state.temporary_damage_resistances,
                *(
                    damage_type
                    for effect in caster.state.timed_effects
                    for damage_type in effect.owned_damage_resistances
                ),
            }
            if option.resistance_damage_type in active_resistances:
                continue
            resource = next(
                (item for item in caster.state.resources if item.id == option.resource_id),
                None,
            )
            if resource is None or resource.current_uses < option.resource_cost:
                continue
            resource.current_uses -= option.resource_cost
            apply_timed_condition(
                caster.state,
                option.id,
                caster.combatant_id,
                source_effect_id=option.id,
                source_template=caster.state.template,
                applied_round=round_number,
                expires_round=round_number + option.duration_rounds,
                expiry_timing="source_turn_start",
                expires_at_start_of_source_turn=True,
                owned_damage_resistances=[option.resistance_damage_type],
                use_default_poison_recovery=False,
            )
            return option
        return None
    except Exception as exc:
        logger.exception("Spell-cast timed resistance failed for %s.", caster.combatant_id)
        raise RuntimeError("Spell-cast timed resistance could not be applied.") from exc

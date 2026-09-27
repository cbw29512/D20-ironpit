from __future__ import annotations

import logging

from app.combat.damage_reaction_events import damage_event_chain
from app.combat.encounter_targeting import combatant_distance
from app.combat.pit_policy import target_order
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.spell_cast_modifiers import ResourceBackedSpellRangeModifier
from app.domain.spells import SpellAttackAction

logger = logging.getLogger(__name__)


def _legal_target(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    spell: SpellAttackAction,
    preferred: EncounterCombatant | None,
    range_modifier: ResourceBackedSpellRangeModifier | None,
) -> EncounterCombatant | None:
    allowed_range = spell.range_ft * (
        range_modifier.range_multiplier if range_modifier is not None else 1
    )
    candidates = []
    if preferred is not None:
        candidates.append(preferred)
    candidates.extend(
        target for target in target_order(caster, setup)
        if preferred is None or target.combatant_id != preferred.combatant_id
    )
    return next(
        (
            target for target in candidates
            if target.side != caster.side
            and target.state.is_alive
            and not target.state.is_dead
            and target.state.current_hp > 0
            and combatant_distance(caster, target) <= allowed_range
        ),
        None,
    )


def resolve_spell_attack_sequence(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    preferred_target: EncounterCombatant,
    spell: SpellAttackAction,
    setup: EncounterSetup,
    turn_key: str,
    dice,
    *,
    slot_level: int = 0,
    range_modifier: ResourceBackedSpellRangeModifier | None = None,
) -> tuple[list[BattleEvent], int]:
    """Resolve one spell cast containing one or more independent spell attacks."""
    try:
        attack_count = spell.attack_count_at_slot(slot_level)
        events: list[BattleEvent] = []
        next_sequence = sequence
        preferred: EncounterCombatant | None = preferred_target

        for index in range(attack_count):
            target = _legal_target(caster, setup, spell, preferred, range_modifier)
            if target is None:
                break
            event = resolve_spell_attack(
                next_sequence,
                round_number,
                caster,
                target,
                spell,
                setup,
                turn_key,
                dice,
                range_modifier=range_modifier,
                cast_slot_level=slot_level if spell.level > 0 else None,
                spend_cast_costs=index == 0,
            )
            chain, next_sequence = damage_event_chain(
                next_sequence + 1,
                round_number,
                caster,
                event,
                setup,
                dice,
                turn_key=turn_key,
            )
            events.extend(chain)
            preferred = target if target.state.current_hp > 0 and not target.state.is_dead else None

        if not events:
            raise ValueError(f"{spell.name} has no legal target for its spell attacks.")
        return events, next_sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Multi-attack spell resolution failed for %s using %s.",
            caster.combatant_id,
            spell.id,
        )
        raise RuntimeError("Multi-attack spell could not be resolved.") from exc

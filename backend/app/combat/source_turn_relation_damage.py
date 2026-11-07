"""Resolve source-turn target relationships with the existing typed damage engine."""
from __future__ import annotations

import logging

from app.combat.damage import roll_damage_component
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.saving_throw_context import SavingThrowContext
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def resolve_source_turn_relation_damage(
    sequence: int, round_number: int, member: EncounterCombatant,
    setup: EncounterSetup, dice,
) -> tuple[list[BattleEvent], int]:
    """At the source's turn start, damage only the live creatures grappling it."""
    try:
        events: list[BattleEvent] = []
        state = member.state
        rules = state.template.source_turn_relation_damages
        if not rules or not state.is_alive or state.is_dead or state.current_hp <= 0:
            return events, sequence
        members = [*setup.heroes, *setup.monsters]
        affected = [item.state for item in members]
        for rule in rules:
            if rule.target_relation not in (
                "creatures_grappling_source", "creatures_grappled_by_source",
            ):
                raise ValueError(f"Unsupported source-turn target relation {rule.target_relation}.")
            for target in members:
                if target.combatant_id == member.combatant_id:
                    continue
                if target.state.is_dead or not target.state.is_alive or target.state.current_hp <= 0:
                    continue
                # The immutable rule selects direction; grapple ownership remains
                # in ordinary fight state. A released/escaped target cannot tick.
                held_state = (state if rule.target_relation == "creatures_grappling_source"
                              else target.state)
                held_owner = (target.combatant_id if rule.target_relation == "creatures_grappling_source"
                              else member.combatant_id)
                active = any(
                    grapple.source_id == held_owner
                    and (rule.required_grapple_condition_id is None
                         or rule.required_grapple_condition_id in grapple.linked_condition_ids)
                    and (grapple.moves_with_source
                         or abs(target.position_ft - member.position_ft) <= grapple.range_ft)
                    for grapple in held_state.grapple_sources
                )
                if not active:
                    continue
                save_roll, saved = None, False
                if rule.save_ability is not None:
                    save_roll, saved = resolve_saving_throw(
                        target.state, rule.save_ability, rule.save_dc,
                        dice, SavingThrowContext(), round_number=round_number,
                        encounter_roller=target, setup=setup,
                    )
                hp_before = target.state.current_hp
                if saved:
                    applied, adjusted = 0, []
                else:
                    component = roll_damage_component(
                        dice, rule.source_name, rule.dice_count, rule.dice_size,
                        rule.damage_bonus, rule.damage_type, False,
                    )
                    applied, adjusted = apply_damage_defenses(target.state, [component])
                    apply_damage(
                        target.state, applied, damage_types={rule.damage_type},
                        dice=dice, affected_states=affected, setup=setup,
                        damage_components=adjusted, source_id=member.combatant_id,
                    )
                events.append(BattleEvent(
                    sequence=sequence, round_number=round_number,
                    event_type="feature", actor_id=member.combatant_id,
                    actor_name=state.template.name, target_id=target.combatant_id,
                    target_name=target.state.template.name,
                    feature_id=rule.source_name, damage_components=adjusted,
                    saving_throw_roll=save_roll,
                    save_ability=rule.save_ability,
                    save_dc=rule.save_dc,
                    save_succeeded=saved if rule.save_ability is not None else None,
                    hp_before=hp_before, hp_after=target.state.current_hp,
                    animation="feature",
                    description=(
                        f"{rule.source_name} deals {applied} {rule.damage_type.value} "
                        f"damage to {target.state.template.name} "
                        f"{'grappling' if rule.target_relation == 'creatures_grappling_source' else 'held by'} "
                        f"{state.template.name}."
                    ),
                ))
                sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Source-turn relationship damage failed for %s.", member.combatant_id)
        raise

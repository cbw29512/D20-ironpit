"""Source-neutral start-of-turn visual saves for timed and staged effects."""
from __future__ import annotations

from collections.abc import Sequence

from app.combat.condition_immunity import condition_is_immune
from app.combat.condition_rules import can_see, is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.source_effect_immunity import (
    grant_source_effect_immunity, has_source_effect_immunity,
)
from app.combat.timed_conditions import apply_timed_condition, remove_effect_group
from app.combat.visual_true_form import observer_sees_true_form
from app.combat.turn_start_visual_policy import (
    VisualTurnStartFacts, decide_visual_turn_start, initiative_precedes,
    resolve_visual_save_stage,
)
from app.combat.visual_source_aversion import record_visual_aversion
from app.content.monster_creature_types import is_creature_type
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def resolve_visual_turn_start_events(
    sequence: int, round_number: int, target: EncounterCombatant,
    setup: EncounterSetup, dice, turn_order: Sequence[str],
) -> tuple[list[BattleEvent], int]:
    """Apply the card-defined effect; never dispatch by monster/ability name."""
    events: list[BattleEvent] = []
    sources = [source for source in [*setup.heroes, *setup.monsters]
               if source.combatant_id != target.combatant_id
               and source.state.template.visual_turn_start_rule is not None]
    sources.sort(key=lambda source: turn_order.index(source.combatant_id))
    for source in sources:
        rule = source.state.template.visual_turn_start_rule
        rider = rule.failed_save_timed_effect
        effect_id = rider.effect_id if rider else rule.terminal_debuff
        if rider and has_source_effect_immunity(target.state, rule.source_id, source.combatant_id):
            continue
        if rider and any(
            effect.source_id == source.combatant_id and effect.source_effect_id == rule.source_id
            and effect.effect_id == rider.effect_id for effect in target.state.timed_effects
        ):
            continue  # Existing timed Frightened effect owns its own end-turn saves.
        distance = combatant_distance(source, target)
        facts = VisualTurnStartFacts(
            distance_ft=distance,
            source_active=source.state.current_hp > 0
                and (not rule.requires_source_not_incapacitated or not is_incapacitated(source.state)),
            target_active=target.state.current_hp > 0 and not target.state.is_dead,
            source_sees_target=can_see(source.state, target.state, distance),
            target_sees_source=can_see(target.state, source.state, distance),
            target_immune=condition_is_immune(target.state, effect_id, source.state.template),
            source_precedes_target=initiative_precedes(
                turn_order, source.combatant_id, target.combatant_id,
            ),
            source_true_form_visible=observer_sees_true_form(source.state, target.state, distance),
            target_type_allowed=not rule.required_target_creature_types or any(
                is_creature_type(target.state.template, kind)
                for kind in rule.required_target_creature_types
            ),
        )
        decision = decide_visual_turn_start(rule, facts)
        if decision == "ineligible":
            continue
        if decision == "averted":
            target.state.visual_aversion_windows = list(record_visual_aversion(
                target.state.visual_aversion_windows, target.combatant_id,
                source.combatant_id, target.state.turns_started,
            ))
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=target.combatant_id, actor_name=target.state.template.name,
                target_id=source.combatant_id, target_name=source.state.template.name,
                feature_id=rule.source_id, animation="condition",
                description=f"{target.state.template.name} averts its eyes from {source.state.template.name}.",
            ))
            sequence += 1
            continue
        roll, succeeded = resolve_saving_throw(
            target.state, rule.save_ability, rule.save_dc, dice,
            round_number=round_number, encounter_roller=target, setup=setup,
        )
        applied: list[str] = []
        removed: list[str] = []
        if rider:
            if succeeded:
                grant_source_effect_immunity(
                    target.state, rule.source_id, source.combatant_id, round_number,
                    source_template=source.state.template,
                )
            else:
                applied_id = apply_timed_condition(
                    target.state, rider.effect_id, source.combatant_id,
                    source_effect_id=rule.source_id,
                    source_template=source.state.template,
                    applied_round=round_number,
                    expires_round=round_number + rider.duration_rounds,
                    expiry_timing=rider.expiry_timing,
                    expires_at_start_of_source_turn=False,
                    repeat_save_ability=rider.repeat_save_ability,
                    repeat_save_dc=rider.repeat_save_dc,
                    repeat_save_timing=rider.repeat_save_timing,
                    repeat_save_disadvantage_while_source_visible=rider.repeat_save_disadvantage_while_source_visible,
                    source_effect_immunity_on_end=rider.source_effect_immunity_on_end,
                    use_default_poison_recovery=False, target_actor=target, setup=setup,
                )
                if applied_id:
                    applied.append(applied_id)
        else:
            current = next((effect for effect in target.state.timed_effects
                if effect.source_id == source.combatant_id
                and effect.source_effect_id == rule.source_id
                and effect.effect_id == rule.initial_debuff), None)
            if not succeeded and roll is None:
                raise ValueError("A failed staged visual save requires a numeric roll.")
            stage = resolve_visual_save_stage(
                rule, rule.save_dc if succeeded else roll.total,
                current.effect_id if current else None,
            )
            if current:
                removed = remove_effect_group(target.state, current)
            if stage != "clear":
                applied_id = apply_timed_condition(
                    target.state, stage, source.combatant_id,
                    source_effect_id=rule.source_id, source_template=source.state.template,
                    applied_round=round_number, expires_at_start_of_source_turn=False,
                    target_actor=target, setup=setup,
                )
                if applied_id:
                    applied.append(applied_id)
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="saving_throw",
            actor_id=source.combatant_id, actor_name=source.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=rule.source_id, save_ability=rule.save_ability,
            save_dc=rule.save_dc, saving_throw_roll=roll, save_succeeded=succeeded,
            applied_condition_ids=applied, removed_condition_ids=removed,
            animation="condition",
            description=f"{target.state.template.name} {'resists' if succeeded else 'fails'} {rule.source_name}.",
        ))
        sequence += 1
        if target.state.is_dead:
            break
    return events, sequence

from __future__ import annotations

from app.combat.action_economy import spend
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.combat.turn_start_reaction_eligibility import eligible_turn_start_reaction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.saving_throw_context import SavingThrowContext


def resolve_turn_start_save_reactions(
    sequence: int,
    round_number: int,
    target: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Trigger one source-owned Reaction per eligible opposing creature."""
    events: list[BattleEvent] = []
    enemies = setup.monsters if target.side == "heroes" else setup.heroes
    for source in enemies:
        if not eligible_turn_start_reaction(source, target):
            continue
        rule = source.state.template.turn_start_save_reaction
        context = SavingThrowContext(
            condition_id=rule.failure_condition,
            effect_tags=frozenset([rule.failure_condition]),
        )
        roll, succeeded = resolve_saving_throw(
            target.state, rule.save_ability, rule.save_dc, dice, context,
            round_number=round_number, encounter_roller=target, setup=setup,
        )
        spend(source.state, "reaction")
        applied = []
        if not succeeded:
            effect = apply_timed_condition(
                target.state, rule.failure_condition, source.combatant_id,
                source_effect_id=rule.source_id, source_template=source.state.template,
                applied_round=round_number, expiry_timing="target_turn_end",
                expires_at_start_of_source_turn=False,
                affected_states=[m.state for m in [*setup.heroes, *setup.monsters]],
            )
            if effect is not None:
                applied.append(effect)
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number,
            event_type="saving_throw", actor_id=target.combatant_id,
            actor_name=target.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            saving_throw_roll=roll, save_ability=rule.save_ability,
            save_dc=rule.save_dc, save_succeeded=succeeded,
            applied_condition_ids=applied, feature_id=rule.source_id,
            animation="condition",
            description=f"{source.state.template.name} uses {rule.source_name} on {target.state.template.name}.",
        ))
        sequence += 1
    return events, sequence

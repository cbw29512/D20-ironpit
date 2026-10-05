from __future__ import annotations

import logging

from app.combat.attack_legality import attack_allowed_against
from app.combat.barrier_line_of_effect import clear_line_between_members
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.exhaustion import gain_exhaustion, reduce_exhaustion
from app.combat.pit_policy import target_order
from app.combat.range import resolve_attack_roll_mode
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.triggered_extra_attacks import TriggeredExtraAttackStack

logger = logging.getLogger(__name__)


def _bloodied(member: EncounterCombatant) -> bool:
    return member.state.current_hp > 0 and member.state.current_hp * 2 <= member.state.template.max_hp


def _legal_target(
    owner: EncounterCombatant,
    setup: EncounterSetup,
    rule: TriggeredExtraAttackStack,
):
    for target in target_order(owner, setup):
        if not clear_line_between_members(owner, target, setup):
            continue
        if not attack_allowed_against(rule.attack, owner.combatant_id, target.state):
            continue
        distance = combatant_distance(owner, target)
        try:
            resolve_attack_roll_mode(rule.attack.weapon, distance, close_enemy_active=False)
        except ValueError:
            continue
        return target, distance
    return None


def _maybe_add_stack(
    member: EncounterCombatant,
    rule: TriggeredExtraAttackStack,
) -> bool:
    state = member.state
    stacks = state.triggered_extra_attack_stack_counts.get(rule.source_id, 0)
    uses = state.feature_use_counts.get(rule.source_id, 0)
    if stacks >= rule.max_stacks or uses >= rule.max_uses:
        return False
    if rule.requires_bloodied and not _bloodied(member):
        return False
    taken = state.damage_taken_this_turn_by_type.get(rule.trigger_damage_type.value, 0)
    if taken < rule.trigger_damage_minimum:
        return False
    state.triggered_extra_attack_stack_counts[rule.source_id] = stacks + 1
    state.feature_use_counts[rule.source_id] = uses + 1
    if rule.exhaustion_per_stack:
        gain_exhaustion(state, rule.exhaustion_per_stack)
        state.source_owned_exhaustion_levels[rule.source_id] = (
            state.source_owned_exhaustion_levels.get(rule.source_id, 0) + rule.exhaustion_per_stack
        )
    return True


def resolve_triggered_extra_attacks_after_turn(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve source-driven post-turn stack triggers and one attack per active stack."""
    try:
        events: list[BattleEvent] = []
        for rule in member.state.template.triggered_extra_attack_stacks:
            added = _maybe_add_stack(member, rule)
            stacks = member.state.triggered_extra_attack_stack_counts.get(rule.source_id, 0)
            if added:
                events.append(BattleEvent(
                    sequence=sequence,
                    round_number=round_number,
                    event_type="feature",
                    actor_id=member.combatant_id,
                    actor_name=member.state.template.name,
                    feature_id=rule.source_id,
                    animation="feature",
                    description=(
                        f"{member.state.template.name} gains one {rule.source_name} stack "
                        f"({stacks}/{rule.max_stacks})."
                    ),
                ))
                sequence += 1
            for _ in range(stacks):
                choice = _legal_target(member, setup, rule)
                if choice is None or member.state.is_dead:
                    break
                target, distance = choice
                event = resolve_encounter_attack(
                    sequence,
                    round_number,
                    member,
                    target,
                    rule.attack,
                    distance,
                    dice,
                    setup,
                    spend_action=False,
                    feature_id=rule.source_id,
                    turn_key=f"{round_number}:{member.combatant_id}:post-turn",
                    allow_reckless=False,
                    close_enemy_active=False,
                    off_turn=True,
                )
                event.description += f" {rule.source_name} makes its attached extra attack."
                events.append(event)
                sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Triggered post-turn extra attacks failed for %s.", member.combatant_id)
        raise


def clear_regeneration_owned_stacks(state) -> list[tuple[str, int]]:
    """Clear stacks and only the Exhaustion levels owned by sources that regrow on healing."""
    cleared: list[tuple[str, int]] = []
    for rule in state.template.triggered_extra_attack_stacks:
        if not rule.clears_on_regeneration_heal:
            continue
        stacks = state.triggered_extra_attack_stack_counts.pop(rule.source_id, 0)
        owned = state.source_owned_exhaustion_levels.pop(rule.source_id, 0)
        if owned:
            reduce_exhaustion(state, owned)
        if stacks:
            cleared.append((rule.source_name, stacks))
    return cleared

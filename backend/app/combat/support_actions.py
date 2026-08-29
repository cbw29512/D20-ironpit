from __future__ import annotations

from app.combat.action_economy import spend
from app.combat.support_effects import apply_support_effect, break_concentration, end_sanctuary
from app.domain.models import BattleEvent, EncounterCombatant, EncounterSetup, SupportAction


def _resource(caster: EncounterCombatant, action: SupportAction):
    if action.resource_id is None:
        return None
    return next((item for item in caster.state.resources if item.id == action.resource_id), None)


def _target_allowed(caster: EncounterCombatant, target: EncounterCombatant, action: SupportAction) -> bool:
    if target.state.is_dead or not target.state.is_alive or target.side != caster.side:
        return False
    if abs(caster.position_ft - target.position_ft) > action.range_ft:
        return False
    if action.target_mode == "self":
        return target.combatant_id == caster.combatant_id
    if action.target_mode == "ally":
        return target.combatant_id != caster.combatant_id
    return True


def resolve_support_action(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    targets: list[EncounterCombatant],
    action: SupportAction,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    if not 1 <= len(targets) <= action.max_targets or len({item.combatant_id for item in targets}) != len(targets):
        raise ValueError("Support action has an illegal target count.")
    if any(not _target_allowed(caster, target, action) for target in targets):
        raise ValueError("Support action has an illegal target.")
    resource = _resource(caster, action)
    if action.resource_id is not None and (resource is None or resource.current_uses < action.resource_cost):
        raise ValueError("Support action resource is unavailable.")
    spend(caster.state, action.action_cost)
    end_sanctuary(caster.state)
    if action.concentration:
        break_concentration(caster.combatant_id, setup)
    if resource is not None:
        resource.current_uses -= action.resource_cost
    events: list[BattleEvent] = []
    for target in targets:
        apply_support_effect(
            target.state, action.effect_id, caster.combatant_id,
            round_number + action.duration_rounds,
            concentration=action.concentration, value=action.save_dc,
        )
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=caster.combatant_id, actor_name=caster.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=action.id, resource_remaining=resource.current_uses if resource else None,
            animation=action.animation,
            description=f"{caster.state.template.name} casts {action.name} on {target.state.template.name}.",
        ))
        sequence += 1
    return events, sequence

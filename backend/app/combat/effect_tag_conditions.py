from app.combat.timed_conditions import apply_timed_condition
from app.domain.events import BattleEvent


def apply_tagged_condition(sequence, round_number, remover, setup, action, effect, remaining):
    grant = effect.grant
    target = effect.target
    hp = target.state.current_hp
    applied = apply_timed_condition(
        target.state, grant.condition_id, remover.combatant_id,
        source_effect_id=action.id, source_template=remover.state.template,
        source_is_magical=True, applied_round=round_number,
        expires_round=round_number + grant.duration_rounds,
        expiry_timing="source_turn_start",
        affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
    )
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=remover.combatant_id, actor_name=remover.state.template.name,
        target_id=target.combatant_id, target_name=target.state.template.name,
        feature_id=action.id, resource_remaining=remaining,
        applied_condition_ids=[applied] if applied else [],
        hp_before=hp, hp_after=target.state.current_hp,
        animation=action.animation,
        description=f"{remover.state.template.name} uses {action.name}: {grant.source_name} "
        f"applies {grant.condition_id} to {target.state.template.name} for {grant.duration_rounds} rounds.",
    )

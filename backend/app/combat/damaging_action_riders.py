from __future__ import annotations

from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent


def resolve_damaging_action_temporary_hp(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    action_id: str,
    events: list[BattleEvent],
) -> BattleEvent | None:
    """Resolve a generic post-damage Temporary HP rider from progression data."""
    rule = actor.state.template.progression_features.damaging_action_temporary_hp_rider
    if rule is None or action_id not in rule.action_ids:
        return None

    dealt_damage = any(
        (component.applied_total or 0) > 0
        for event in events
        for component in event.damage_components
    )
    if not dealt_damage:
        return None

    scores = actor.state.template.ability_scores
    if scores is None:
        raise ValueError("Ability-scaled Temporary HP requires ability scores.")

    amount = max(0, scores.modifier(rule.ability) * rule.multiplier)
    before = actor.state.temporary_hp
    after = grant_temporary_hit_points(actor.state, amount)
    if after <= before:
        return None

    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=actor.combatant_id,
        actor_name=actor.state.template.name,
        target_id=actor.combatant_id,
        target_name=actor.state.template.name,
        temporary_hp_before=before,
        temporary_hp_after=after,
        feature_id=rule.source_id,
        animation="temporary-hp",
        description=(
            f"{actor.state.template.name} gains {after - before} Temporary HP "
            f"from {rule.source_id.replace('-', ' ').title()}."
        ),
    )

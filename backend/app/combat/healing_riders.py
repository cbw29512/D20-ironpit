from __future__ import annotations

from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, HealingAction


def _slot_level(action: HealingAction) -> int | None:
    if not action.resource_id or not action.resource_id.startswith("spell-slot-"):
        return None
    return int(action.resource_id.removeprefix("spell-slot-"))


def apply_slot_healing_self_rider(
    sequence: int,
    round_number: int,
    healer: EncounterCombatant,
    healed_other: bool,
    action: HealingAction,
) -> BattleEvent | None:
    rule = healer.state.template.progression_features.slot_healing_other_self_rider
    slot_level = _slot_level(action)
    if rule is None or slot_level is None or not healed_other:
        return None
    amount = rule.flat_bonus + rule.per_slot_level * slot_level
    before = healer.state.current_hp
    restored = restore_hit_points(healer.state, amount)
    if restored <= 0:
        return None
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="healing",
        actor_id=healer.combatant_id, actor_name=healer.state.template.name,
        target_id=healer.combatant_id, target_name=healer.state.template.name,
        hp_before=before, hp_after=healer.state.current_hp,
        death_save_successes=healer.state.death_save_successes,
        death_save_failures=healer.state.death_save_failures,
        is_stable=healer.state.is_stable, is_dead=healer.state.is_dead,
        feature_id=rule.source_id, animation="healing",
        description=f"{healer.state.template.name} restores {restored} HP from {rule.source_id.replace('-', ' ').title()}.",
    )

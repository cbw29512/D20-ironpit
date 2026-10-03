from __future__ import annotations

from app.combat.encounter_targeting import combatant_distance
from app.combat.action_economy import spend
from app.combat.friendly_area import best_friendly_area_placement
from app.combat.healing_policy import healing_rider_worthwhile, resource_available, slot_heal, target_allowed
from app.combat.healing_resolution_support import apply_healing_riders, resolve_healing_amount
from app.combat.hit_points import effective_max_hp
from app.combat.spellcasting import mark_slot_spell_cast
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DiceRoll, HealingAction


def choose_group_healing_targets(
    healer: EncounterCombatant,
    setup: EncounterSetup,
    action: HealingAction,
    turn_key: str | None = None,
) -> list[EncounterCombatant]:
    if action.max_targets <= 1 or not resource_available(healer, action, turn_key):
        return []
    allies = setup.heroes if healer.side == "heroes" else setup.monsters
    legal = [target for target in allies if target_allowed(healer, target, action)]
    legal.sort(key=lambda target: (
        target.state.current_hp > 0,
        target.state.current_hp / max(1, effective_max_hp(target.state)),
        target.combatant_id,
    ))
    worthwhile = [
        target for target in legal
        if target.state.current_hp == 0
        or target.state.current_hp * 2 <= effective_max_hp(target.state)
        or healing_rider_worthwhile(target, action)
    ]
    if action.secondary_target_within_ft is not None and worthwhile:
        primary = worthwhile[0]
        linked = [
            target for target in worthwhile[1:]
            if combatant_distance(target, primary) <= action.secondary_target_within_ft
        ]
        worthwhile = [primary, *linked]
    if action.area_radius_ft is not None:
        placement = best_friendly_area_placement(
            healer,
            setup,
            action.area_radius_ft,
            action.range_ft,
            {target.combatant_id for target in worthwhile},
        )
        if placement is None:
            return []
        allowed_ids = set(placement.target_ids)
        worthwhile = [target for target in worthwhile if target.combatant_id in allowed_ids]
    return worthwhile[:action.max_targets]


def resolve_group_healing(
    sequence: int,
    round_number: int,
    healer: EncounterCombatant,
    targets: list[EncounterCombatant],
    action: HealingAction,
    dice,
    turn_key: str | None = None,
    *,
    setup: EncounterSetup | None = None,
) -> tuple[list[BattleEvent], int]:
    if action.max_targets <= 1 or not targets or len(targets) > action.max_targets:
        raise ValueError("Group healing requires one or more legal targets within max_targets.")
    if any(not target_allowed(healer, target, action) for target in targets):
        raise ValueError("Group healing contains an illegal target.")
    if action.secondary_target_within_ft is not None and len(targets) > 1:
        primary = targets[0]
        if any(
            combatant_distance(target, primary) > action.secondary_target_within_ft
            for target in targets[1:]
        ):
            raise ValueError("Group healing secondary targets violate linked-target distance.")
    if action.area_radius_ft is not None:
        if setup is None:
            raise ValueError("Area group healing requires the actual encounter setup.")
        target_ids = {target.combatant_id for target in targets}
        placement = best_friendly_area_placement(
            healer,
            setup,
            action.area_radius_ft,
            action.range_ft,
            target_ids,
            required_ids=target_ids,
        )
        if placement is None:
            raise ValueError("Group healing targets do not fit one legal healing area.")
    if not resource_available(healer, action, turn_key):
        raise ValueError("Group healing resource is unavailable.")
    if slot_heal(action):
        if turn_key is None:
            raise ValueError("Spell-slot group healing requires an active turn key.")
        mark_slot_spell_cast(healer.state, turn_key)
    spend(healer.state, action.action_cost)
    remaining = None
    if action.resource_id is not None:
        resource = next(item for item in healer.state.resources if item.id == action.resource_id)
        resource.current_uses -= action.resource_cost
        remaining = resource.current_uses
    events: list[BattleEvent] = []
    for target in targets:
        before = target.state.current_hp
        rolls, total, healed, notation, modifier = resolve_healing_amount(
            healer, target, action, dice,
        )
        removed = apply_healing_riders(target, action)
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="healing",
            actor_id=healer.combatant_id, actor_name=healer.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            healing_roll=DiceRoll(notation=notation, rolls=rolls, modifier=modifier, total=total),
            hp_before=before, hp_after=target.state.current_hp,
            death_save_successes=target.state.death_save_successes,
            death_save_failures=target.state.death_save_failures,
            is_stable=target.state.is_stable, is_dead=target.state.is_dead,
            feature_id=action.id, resource_remaining=remaining, animation=action.animation,
            removed_condition_ids=removed,
            description=(
                f"{healer.state.template.name} uses {action.name} on {target.state.template.name} "
                f"and restores {healed} HP."
                + (
                    " Conditions ended: "
                    + ", ".join(item.replace("_", " ").title() for item in removed)
                    + "."
                    if removed else ""
                )
            ),
        ))
        sequence += 1
    return events, sequence

from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.area_targeting import AreaPlacement, member_in_area_placement
from app.combat.grapple_queries import source_has_active_grapple
from app.combat.hit_points import effective_max_hp
from app.combat.resources import action_resource_available, spend_action_resource
from app.combat.save_targets import resolve_save_targets
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DiceRoll, SavingThrowAction

logger = logging.getLogger(__name__)


def _area_healing_target(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
    placement: AreaPlacement,
    *,
    require_wounded: bool,
) -> EncounterCombatant | None:
    try:
        rider = action.area_healing_rider
        if rider is None or action.area is None:
            return None
        allies = setup.heroes if actor.side == "heroes" else setup.monsters
        legal = [
            member for member in allies
            if member.state.is_alive and not member.state.is_dead
            and member_in_area_placement(actor, member, action.area, placement)
            and (not require_wounded or member.state.current_hp < effective_max_hp(member.state))
        ]
        if not legal:
            return None
        return min(
            legal,
            key=lambda member: (
                member.state.current_hp > 0,
                member.state.current_hp / max(1, effective_max_hp(member.state)),
                member.combatant_id,
            ),
        )
    except Exception:
        logger.exception("Failed to choose area-healing target for %s.", action.id)
        raise


def _resolve_area_healing(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    dice,
    resource_remaining: int | None,
) -> tuple[BattleEvent, int]:
    try:
        rider = action.area_healing_rider
        if rider is None:
            raise ValueError(f"{action.name} has no area-healing rider.")
        rolls = [dice.roll(rider.dice_size) for _ in range(rider.dice_count)]
        total = sum(rolls) + rider.healing_bonus
        before = target.state.current_hp
        healed = restore_hit_points(target.state, total)
        event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="healing",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            healing_roll=DiceRoll(
                notation=f"{rider.dice_count}d{rider.dice_size}+{rider.healing_bonus}",
                rolls=rolls,
                modifier=rider.healing_bonus,
                total=total,
            ),
            hp_before=before,
            hp_after=target.state.current_hp,
            death_save_successes=target.state.death_save_successes,
            death_save_failures=target.state.death_save_failures,
            is_stable=target.state.is_stable,
            is_dead=target.state.is_dead,
            feature_id=action.id,
            resource_remaining=resource_remaining,
            animation=action.animation,
            description=(
                f"{actor.state.template.name}'s {action.name} restores {healed} HP "
                f"to {target.state.template.name}."
            ),
        )
        return event, sequence + 1
    except Exception:
        logger.exception("Failed area-healing rider for %s.", action.id)
        raise


def choose_area_save(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    *,
    action_cost: str | None = None,
) -> tuple[SavingThrowAction, AreaPlacement] | None:
    try:
        candidates = []
        for action in actor.state.template.saving_throw_actions:
            if action_cost is not None and action.action_cost != action_cost:
                continue
            if action.area is None or not action_resource_available(actor.state, action):
                continue
            if action.requires_no_active_grapple and source_has_active_grapple(setup, actor.combatant_id):
                continue
            for placement in legal_area_save_placements(actor, setup, action):
                heal_target = _area_healing_target(
                    actor, setup, action, placement,
                    require_wounded=not placement.target_ids,
                )
                if action.area_healing_rider is not None and heal_target is None:
                    continue
                candidates.append((action, placement, heal_target))
        if not candidates:
            return None
        action, placement, _ = max(
            candidates,
            key=lambda item: (
                len(item[1].target_ids),
                item[0].damage_dice_count,
                item[2] is not None,
                item[0].id,
            ),
        )
        return action, placement
    except Exception:
        logger.exception("Failed to choose area save action for %s.", actor.combatant_id)
        raise


def resolve_area_save(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
    placement: AreaPlacement,
    dice,
) -> tuple[list[BattleEvent], int]:
    try:
        if action.area is None:
            raise ValueError(f"{action.name} has no area geometry.")
        if not is_available(actor.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is not available for {action.name}.")
        if not action_resource_available(actor.state, action):
            raise ValueError(f"{action.name} resource is unavailable.")
        legal = legal_area_save_placements(actor, setup, action)
        if placement not in legal:
            raise ValueError(f"{action.name} has a stale or illegal area placement.")
        heal_target = _area_healing_target(
            actor, setup, action, placement,
            require_wounded=not placement.target_ids,
        )
        if action.area_healing_rider is not None and heal_target is None:
            raise ValueError(f"{action.name} has no legal healing target in its area.")

        spend(actor.state, action.action_cost)
        if placement.target_ids:
            events, sequence = resolve_save_targets(
                sequence, round_number, actor, setup, action,
                placement.target_ids, dice, skip_range_check=True,
            )
            remaining = events[0].resource_remaining if events else None
        else:
            remaining = spend_action_resource(actor.state, action)
            events = []

        if heal_target is not None:
            event, sequence = _resolve_area_healing(
                sequence, round_number, actor, heal_target, action, dice, remaining,
            )
            events.append(event)
        return events, sequence
    except Exception:
        logger.exception("Failed area save action %s for %s.", action.id, actor.combatant_id)
        raise

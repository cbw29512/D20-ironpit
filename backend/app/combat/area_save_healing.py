from __future__ import annotations

import logging

from app.combat.area_targeting import AreaPlacement, member_in_area_placement
from app.combat.hit_points import effective_max_hp
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DiceRoll, SavingThrowAction

logger = logging.getLogger(__name__)


def choose_area_healing_target(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
    placement: AreaPlacement,
    *,
    require_wounded: bool,
) -> EncounterCombatant | None:
    try:
        if action.area_healing_rider is None or action.area is None:
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


def resolve_area_healing(
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
            sequence=sequence, round_number=round_number, event_type="healing",
            actor_id=actor.combatant_id, actor_name=actor.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            healing_roll=DiceRoll(
                notation=f"{rider.dice_count}d{rider.dice_size}+{rider.healing_bonus}",
                rolls=rolls, modifier=rider.healing_bonus, total=total,
            ),
            hp_before=before, hp_after=target.state.current_hp,
            death_save_successes=target.state.death_save_successes,
            death_save_failures=target.state.death_save_failures,
            is_stable=target.state.is_stable, is_dead=target.state.is_dead,
            feature_id=action.id, resource_remaining=resource_remaining,
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

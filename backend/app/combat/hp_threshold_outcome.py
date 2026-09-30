"""Shared threshold outcome application, separated from legality and resource selection."""
import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.instant_death import apply_instant_death
from app.combat.zero_hp import apply_damage
from app.combat.zero_hp_replacement import consume_zero_hp_replacement_log
from app.domain.models import BattleEvent, DamageRollComponent, DamageType, DiceRoll


def resolve_threshold_target(sequence, round_number, actor, target, action, setup, remaining, dice):
    try:
        hp_before = target.state.current_hp
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        damage_roll = None
        damage_components = []
        prevented = False
        fallback = target.state.current_hp > action.max_current_hp
        if fallback:
            if dice is None:
                raise ValueError(f"{action.name} fallback damage requires dice context.")
            rolls = [dice.roll(action.fallback_damage_dice_size) for _ in range(action.fallback_damage_dice_count)]
            raw_total = sum(rolls) + action.fallback_damage_bonus
            damage_type = DamageType(action.fallback_damage_type)
            raw = DamageRollComponent(
                source=action.name,
                notation=f"{action.fallback_damage_dice_count}d{action.fallback_damage_dice_size}"
                + (f"+{action.fallback_damage_bonus}" if action.fallback_damage_bonus else ""),
                rolls=rolls,
                modifier=action.fallback_damage_bonus,
                damage_type=damage_type,
                total=raw_total,
            )
            applied_total, damage_components = apply_damage_defenses(target.state, [raw])
            if applied_total:
                apply_damage(
                    target.state, applied_total, damage_types={damage_type}, dice=dice,
                    affected_states=affected_states,
                )
            damage_roll = DiceRoll(
                notation=raw.notation, rolls=rolls, modifier=action.fallback_damage_bonus,
                total=applied_total,
            )
        else:
            prevented = apply_instant_death(target.state, affected_states=affected_states) == "instant_death_prevented"
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=actor.combatant_id, actor_name=actor.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            hp_before=hp_before, hp_after=target.state.current_hp, is_dead=target.state.is_dead,
            damage_roll=damage_roll, damage_components=damage_components,
            feature_id=action.id, resource_remaining=remaining, animation=action.animation,
            description=(
                f"{actor.state.template.name} uses {action.name} on {target.state.template.name}; "
                + (
                    f"{target.state.template.name} takes {damage_roll.total} {action.fallback_damage_type.title()} damage."
                    if fallback else (
                        f"{target.state.template.name} dies."
                        if not prevented else f"{target.state.template.name}'s ward negates the instant-death effect."
                    )
                )
                + consume_zero_hp_replacement_log(target.state)
            ),
        )
    except Exception:
        logging.getLogger(__name__).exception("Threshold outcome failed for %s against %s.", actor.combatant_id, target.combatant_id)
        raise

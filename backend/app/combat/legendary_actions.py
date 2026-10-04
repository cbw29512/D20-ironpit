from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.legendary_action_choice import choose_legendary_action, choose_legendary_attack
from app.combat.modifier_stack import add_modifier
from app.combat.resources import spend_resource
from app.combat.save_targets import resolve_save_targets
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DiceRoll
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)
RESOURCE_ID = "legendary-actions"


def resolve_legendary_actions_after_turn(
    sequence: int,
    round_number: int,
    just_acted: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Each other combatant may spend one legendary action option after this turn."""
    try:
        events: list[BattleEvent] = []
        others = [
            item for item in [*setup.heroes, *setup.monsters]
            if item.combatant_id != just_acted.combatant_id
        ]
        for actor in others:
            choice = choose_legendary_action(actor, setup)
            if choice is None:
                continue
            kind, selected = choice
            option = selected[0] if isinstance(selected, tuple) else selected
            spend_resource(actor.state, RESOURCE_ID, option.cost)
            prefix = f"{actor.state.template.name} uses Legendary Action: {option.name}."
            if kind == "attack":
                option, target, attack = selected
                event = resolve_attack(
                    sequence, round_number, actor.state, target.state, attack,
                    combatant_distance(actor, target), dice,
                    actor_event_id=actor.combatant_id, target_event_id=target.combatant_id,
                    spend_action=False, off_turn=True, feature_id=option.id,
                    affected_states=[item.state for item in [*setup.heroes, *setup.monsters]],
                    reaction_setup=setup, reaction_roller=actor,
                )
                events.append(event.model_copy(update={
                    "description": f"{prefix} {event.description}",
                }))
                sequence += 1
                continue
            if kind == "save":
                option, action, placement = selected
                resolved, sequence = resolve_save_targets(
                    sequence, round_number, actor, setup, action, placement.target_ids, dice,
                    skip_range_check=True,
                )
                for event in resolved:
                    events.append(event.model_copy(update={
                        "description": f"{prefix} {event.description}",
                        "feature_id": option.id,
                    }))
                continue
            if kind == "heal":
                spec = option.heal
                if spec is None:
                    raise ValueError(f"{actor.state.template.name} legendary heal {option.id} is missing a spec.")
                rolls = [dice.roll(spec.dice_size) for _ in range(spec.dice_count)]
                total = sum(rolls) + spec.healing_bonus
                before = actor.state.current_hp
                healed = restore_hit_points(actor.state, total)
                events.append(BattleEvent(
                    sequence=sequence,
                    round_number=round_number,
                    event_type="healing",
                    actor_id=actor.combatant_id,
                    actor_name=actor.state.template.name,
                    target_id=actor.combatant_id,
                    target_name=actor.state.template.name,
                    healing_roll=DiceRoll(
                        notation=f"{spec.dice_count}d{spec.dice_size}+{spec.healing_bonus}",
                        rolls=rolls,
                        modifier=spec.healing_bonus,
                        total=total,
                    ),
                    hp_before=before,
                    hp_after=actor.state.current_hp,
                    feature_id=option.id,
                    animation="healing",
                    description=f"{prefix} {actor.state.template.name} regains {healed} HP.",
                ))
                sequence += 1
                continue
            if kind == "ac_buff":
                option, target = selected
                spec = option.ac_buff
                if spec is None:
                    raise ValueError(f"{actor.state.template.name} legendary AC buff {option.id} is missing a spec.")
                add_modifier(target.state, CombatModifier(
                    id=f"{actor.combatant_id}:{option.id}:{target.combatant_id}",
                    source_id=actor.combatant_id,
                    source_effect_id=option.id,
                    source_name=option.name,
                    source_is_magical=True,
                    kind=ModifierKind.ARMOR_CLASS,
                    flat_bonus=spec.ac_bonus,
                    expires_source_turn_end_round=round_number,
                ))
                events.append(BattleEvent(
                    sequence=sequence,
                    round_number=round_number,
                    event_type="feature",
                    actor_id=actor.combatant_id,
                    actor_name=actor.state.template.name,
                    target_id=target.combatant_id,
                    target_name=target.state.template.name,
                    feature_id=option.id,
                    animation="buff",
                    description=(
                        f"{prefix} {target.state.template.name} gains +{spec.ac_bonus} AC "
                        f"until the end of {actor.state.template.name}'s next turn."
                    ),
                ))
                sequence += 1
                continue
            if kind == "check":
                from app.combat.ability_check_escape import ability_check_bonus
                from app.combat.ability_checks import ability_check_roll_mode, resolve_ability_check_outcome
                from app.combat.exhaustion import d20_modifier
                from app.combat.rolls import roll_d20
                ability = option.check_ability
                if ability is None:
                    raise ValueError(f"{actor.state.template.name} legendary check {option.id} is missing ability.")
                check = roll_d20(
                    dice,
                    ability_check_bonus(actor.state, ability) + d20_modifier(actor.state),
                    ability_check_roll_mode(actor.state),
                )
                check, _ = resolve_ability_check_outcome(
                    actor.state, ability, check, 10, dice=dice, round_number=round_number,
                    encounter_roller=actor, setup=setup,
                )
                events.append(BattleEvent(
                    sequence=sequence,
                    round_number=round_number,
                    event_type="feature",
                    actor_id=actor.combatant_id,
                    actor_name=actor.state.template.name,
                    ability_check_roll=check,
                    check_ability=ability,
                    feature_id=option.id,
                    animation="check",
                    description=f"{prefix} {actor.state.template.name} makes a {ability.title()} check.",
                ))
                sequence += 1
                continue
            raise ValueError(f"{actor.state.template.name} legendary action {option.id} uses unsupported kind {kind!r}.")
        return events, sequence
    except Exception:
        logger.exception("Failed legendary actions after %s.", just_acted.combatant_id)
        raise


__all__ = [
    "choose_legendary_attack",
    "choose_legendary_action",
    "resolve_legendary_actions_after_turn",
]

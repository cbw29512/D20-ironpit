from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.cleric_channel_policy import ChannelDivinityChoice
from app.combat.cleric_divine_spark import resolve_divine_spark
from app.combat.cleric_preserve_life import resolve_preserve_life
from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.content.monster_creature_types import is_creature_type
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

CHANNEL_DIVINITY = "channel-divinity"
TURN_UNDEAD = "turn-undead"
TURNED_EFFECT = "turned-undead"


def _resource(cleric: EncounterCombatant):
    resource = next((item for item in cleric.state.resources if item.id == CHANNEL_DIVINITY), None)
    if resource is None or resource.current_uses < 1:
        raise ValueError("Channel Divinity has no remaining use.")
    return resource


def _spell_save_dc(cleric: EncounterCombatant) -> int:
    dcs = {action.dc for action in cleric.state.template.spell_save_actions}
    if len(dcs) != 1:
        raise ValueError("Channel Divinity requires one certified Cleric spell save DC.")
    return dcs.pop()


def _spend_channel(cleric: EncounterCombatant) -> int:
    if not is_available(cleric.state, "action"):
        raise ValueError("Channel Divinity requires an available action.")
    resource = _resource(cleric)
    spend(cleric.state, "action")
    resource.current_uses -= 1
    return resource.current_uses


def _apply_turn_effects(
    cleric: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
    round_number: int,
) -> list[str]:
    states = [member.state for member in [*setup.heroes, *setup.monsters]]
    common = dict(
        source_effect_id=TURN_UNDEAD,
        applied_round=round_number,
        expires_round=round_number + 10,
        expiry_timing="source_turn_start",
        affected_states=states,
        ends_on_damage=True,
        ends_if_source_incapacitated=True,
        ends_if_source_dead=True,
    )
    applied = [
        apply_timed_condition(
            target.state, TURNED_EFFECT, cleric.combatant_id,
            turn_behavior="forced_retreat", **common,
        )
    ]
    for condition in ("frightened", "incapacitated"):
        if not condition_is_immune(target.state, condition):
            applied.append(apply_timed_condition(target.state, condition, cleric.combatant_id, **common))
    return [effect for effect in applied if effect is not None]


def resolve_turn_undead(
    sequence: int,
    round_number: int,
    cleric: EncounterCombatant,
    setup: EncounterSetup,
    targets: tuple[EncounterCombatant, ...],
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    if not targets:
        raise ValueError("Turn Undead requires at least one legal Undead target.")
    for target in targets:
        if abs(cleric.position_ft - target.position_ft) > 30 or not is_creature_type(target.state.template, "undead"):
            raise ValueError("Turn Undead targets must be Undead within 30 feet.")
    dc = _spell_save_dc(cleric)
    remaining = _spend_channel(cleric)
    events: list[BattleEvent] = []
    for target in targets:
        roll, succeeded = resolve_saving_throw(target.state, "wisdom", dc, dice)
        applied = [] if succeeded else _apply_turn_effects(cleric, target, setup, round_number)
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="saving_throw",
            actor_id=cleric.combatant_id, actor_name=cleric.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            saving_throw_roll=roll, save_ability="wisdom", save_dc=dc, save_succeeded=succeeded,
            applied_condition_ids=applied, feature_id=TURN_UNDEAD, resource_remaining=remaining,
            animation="turn-undead",
            description=f"{target.state.template.name} {'resists' if succeeded else 'fails'} {cleric.state.template.name}'s Turn Undead.",
        ))
        sequence += 1
    return events, sequence


def resolve_channel_divinity(
    sequence: int,
    round_number: int,
    cleric: EncounterCombatant,
    setup: EncounterSetup,
    choice: ChannelDivinityChoice,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    if choice.kind == "turn-undead":
        return resolve_turn_undead(sequence, round_number, cleric, setup, choice.targets, dice)
    remaining = _spend_channel(cleric)
    if choice.kind == "preserve-life":
        return [resolve_preserve_life(sequence, round_number, cleric, choice.targets, remaining)], sequence + 1
    event = resolve_divine_spark(
        sequence, round_number, cleric, choice.targets[0], setup, dice,
        healing=choice.kind == "divine-spark-heal",
        save_dc=_spell_save_dc(cleric), resource_remaining=remaining,
    )
    return [event], sequence + 1

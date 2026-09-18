from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.cleric_channel_policy import ChannelDivinityChoice
from app.combat.cleric_divine_spark import resolve_divine_spark
from app.combat.cleric_preserve_life import resolve_preserve_life
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.turn_creature_effects import resolve_turning_saves
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
        if combatant_distance(cleric, target) > 30 or not is_creature_type(target.state.template, "undead"):
            raise ValueError("Turn Undead targets must be Undead within 30 feet.")
    dc = _spell_save_dc(cleric)
    remaining = _spend_channel(cleric)
    return resolve_turning_saves(
        sequence, round_number, cleric, setup, targets, dice,
        save_dc=dc, source_effect_id=TURN_UNDEAD, turned_effect_id=TURNED_EFFECT,
        resource_remaining=remaining, feature_name="Turn Undead",
    )


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

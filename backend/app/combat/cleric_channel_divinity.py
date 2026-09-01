from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.cleric_channel_policy import ChannelDivinityChoice
from app.combat.condition_immunity import condition_is_immune
from app.combat.damage_defenses import adjusted_damage_amount, apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage, restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent, DamageType, DiceRoll

CHANNEL_DIVINITY = "channel-divinity"
TURN_UNDEAD = "turn-undead"
DIVINE_SPARK = "divine-spark"


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


def _turn_conditions(
    cleric: EncounterCombatant, target: EncounterCombatant, setup: EncounterSetup,
    round_number: int, dc: int,
) -> list[str]:
    candidates = [name for name in ("frightened", "incapacitated") if not condition_is_immune(target.state, name)]
    if not candidates:
        return []
    anchor = candidates[0]
    states = [member.state for member in [*setup.heroes, *setup.monsters]]
    applied: list[str] = []
    for condition in candidates:
        is_anchor = condition == anchor
        result = apply_timed_condition(
            target.state, condition, cleric.combatant_id,
            source_effect_id=TURN_UNDEAD,
            applied_round=round_number,
            expires_round=round_number + 10,
            expiry_timing="source_turn_start",
            repeat_save_ability="wisdom" if is_anchor else None,
            repeat_save_dc=dc if is_anchor else None,
            repeat_save_timing="target_turn_end" if is_anchor else None,
            affected_states=states,
            turn_behavior="forced_retreat" if is_anchor else "normal",
            ends_on_damage=True,
            ends_if_source_incapacitated=True,
            ends_if_source_dead=True,
        )
        if result is not None:
            applied.append(result)
    return applied


def resolve_turn_undead(
    sequence: int, round_number: int, cleric: EncounterCombatant,
    setup: EncounterSetup, targets: tuple[EncounterCombatant, ...], dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    dc = _spell_save_dc(cleric)
    remaining = _spend_channel(cleric)
    events: list[BattleEvent] = []
    for target in targets:
        roll, succeeded = resolve_saving_throw(target.state, "wisdom", dc, dice)
        applied = [] if succeeded else _turn_conditions(cleric, target, setup, round_number, dc)
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="saving_throw",
            actor_id=cleric.combatant_id, actor_name=cleric.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            saving_throw_roll=roll, save_ability="wisdom", save_dc=dc, save_succeeded=succeeded,
            applied_condition_ids=applied, feature_id=TURN_UNDEAD, resource_remaining=remaining,
            animation="turn-undead",
            description=(f"{target.state.template.name} {'resists' if succeeded else 'fails'} "
                         f"{cleric.state.template.name}'s Turn Undead."),
        ))
        sequence += 1
    return events, sequence


def _spark_damage_type(target: EncounterCombatant) -> DamageType:
    radiant = adjusted_damage_amount(2, DamageType.RADIANT, target.state)
    necrotic = adjusted_damage_amount(2, DamageType.NECROTIC, target.state)
    return DamageType.RADIANT if radiant >= necrotic else DamageType.NECROTIC


def resolve_divine_spark(
    sequence: int, round_number: int, cleric: EncounterCombatant, target: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider, *, healing: bool,
) -> BattleEvent:
    if target.combatant_id == cleric.combatant_id or abs(cleric.position_ft - target.position_ft) > 30:
        raise ValueError("Divine Spark requires another creature within 30 feet.")
    remaining = _spend_channel(cleric)
    roll = dice.roll(8)
    total = roll + 3
    notation = "1d8+3"
    if healing:
        before = target.state.current_hp
        healed = restore_hit_points(target.state, total)
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="healing",
            actor_id=cleric.combatant_id, actor_name=cleric.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            healing_roll=DiceRoll(notation=notation, rolls=[roll], modifier=3, total=total),
            hp_before=before, hp_after=target.state.current_hp, feature_id=DIVINE_SPARK,
            resource_remaining=remaining, animation="divine-spark",
            description=f"{cleric.state.template.name} restores {healed} HP with Divine Spark.",
        )
    dc = _spell_save_dc(cleric)
    save, succeeded = resolve_saving_throw(target.state, "constitution", dc, dice)
    resolved = total // 2 if succeeded else total
    damage_type = _spark_damage_type(target)
    component = DamageRollComponent(
        source="Divine Spark", notation=notation, rolls=[roll], modifier=3,
        damage_type=damage_type, total=resolved,
    )
    applied_total, components = apply_damage_defenses(target.state, [component])
    before = target.state.current_hp
    if applied_total:
        states = [member.state for member in [*setup.heroes, *setup.monsters]]
        apply_damage(target.state, applied_total, damage_types={damage_type}, dice=dice, affected_states=states)
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="saving_throw",
        actor_id=cleric.combatant_id, actor_name=cleric.state.template.name,
        target_id=target.combatant_id, target_name=target.state.template.name,
        saving_throw_roll=save, save_ability="constitution", save_dc=dc, save_succeeded=succeeded,
        damage_roll=DiceRoll(notation=notation, rolls=[roll], modifier=3, total=applied_total),
        damage_components=components, hp_before=before, hp_after=target.state.current_hp,
        feature_id=DIVINE_SPARK, resource_remaining=remaining, animation="divine-spark",
        description=f"{target.state.template.name} takes {applied_total} {damage_type.value} damage from Divine Spark.",
    )


def resolve_channel_divinity(
    sequence: int, round_number: int, cleric: EncounterCombatant, setup: EncounterSetup,
    choice: ChannelDivinityChoice, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    if choice.kind == "turn-undead":
        return resolve_turn_undead(sequence, round_number, cleric, setup, choice.targets, dice)
    event = resolve_divine_spark(
        sequence, round_number, cleric, choice.targets[0], setup, dice,
        healing=choice.kind == "divine-spark-heal",
    )
    return [event], sequence + 1

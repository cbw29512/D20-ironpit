from app.combat.cleric_channel_divinity import resolve_channel_divinity
from app.combat.cleric_channel_policy import ChannelDivinityChoice, choose_channel_divinity
from app.combat.dice import FixedDiceProvider
from app.combat.ongoing_spell_control import forced_retreat_active
from app.combat.source_bound_effects import cleanup_disabled_source_effects
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import expire_start_of_turn_conditions
from app.combat.zero_hp import apply_damage
from app.content.audited_cleric import build_seraphine_dawnshield_level_two
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_registry import build_combatant_from_capabilities
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup() -> tuple[EncounterSetup, EncounterCombatant, EncounterCombatant, EncounterCombatant]:
    cleric = _member(build_seraphine_dawnshield_level_two(), "cleric", "heroes", 0)
    skeleton = _member(build_combatant_from_capabilities("srd-skeleton"), "skeleton", "monsters", 10)
    zombie = _member(build_combatant_from_capabilities("srd-ogre-zombie"), "zombie", "monsters", 15)
    setup = EncounterSetup(
        heroes=[cleric], monsters=[skeleton, zombie], hero_total_levels=2, monster_total_cr="2 1/4",
    )
    return setup, cleric, skeleton, zombie


def _channel_uses(cleric: EncounterCombatant) -> int:
    return next(item.current_uses for item in cleric.state.resources if item.id == "channel-divinity")


def test_level_two_policy_turns_every_legal_undead_before_spending_spell_slots() -> None:
    setup, cleric, skeleton, zombie = _setup()
    choice = choose_channel_divinity(cleric, setup)
    assert choice is not None
    assert choice.kind == "turn-undead"
    assert choice.targets == (skeleton, zombie)
    assert _channel_uses(cleric) == 2


def test_turn_undead_uses_one_initial_save_and_no_repeat_save() -> None:
    setup, cleric, skeleton, zombie = _setup()
    choice = ChannelDivinityChoice("turn-undead", (skeleton, zombie))
    events, sequence = resolve_channel_divinity(1, 1, cleric, setup, choice, FixedDiceProvider([1, 1]))

    assert sequence == 3
    assert [event.feature_id for event in events] == ["turn-undead", "turn-undead"]
    assert [event.save_succeeded for event in events] == [False, False]
    assert _channel_uses(cleric) == 1
    assert cleric.state.action_available is False
    for target in (skeleton, zombie):
        assert {"turned-undead", "frightened", "incapacitated"}.issubset(target.state.active_effect_ids)
        assert forced_retreat_active(target.state) is True
        assert all(effect.repeat_save_timing is None for effect in target.state.timed_effects)
        assert {effect.expires_round for effect in target.state.timed_effects} == {11}


def test_turn_undead_ends_as_a_group_on_damage() -> None:
    setup, cleric, skeleton, _ = _setup()
    resolve_channel_divinity(
        1, 1, cleric, setup, ChannelDivinityChoice("turn-undead", (skeleton,)), FixedDiceProvider([1]),
    )
    apply_damage(skeleton.state, 1)
    assert not {"turned-undead", "frightened", "incapacitated"}.intersection(skeleton.state.active_effect_ids)
    assert skeleton.state.timed_effects == []


def test_turn_undead_ends_when_cleric_is_incapacitated() -> None:
    setup, cleric, skeleton, _ = _setup()
    resolve_channel_divinity(
        1, 1, cleric, setup, ChannelDivinityChoice("turn-undead", (skeleton,)), FixedDiceProvider([1]),
    )
    cleric.state.active_effect_ids.append("incapacitated")
    cleanup_disabled_source_effects(setup)
    assert skeleton.state.timed_effects == []
    assert forced_retreat_active(skeleton.state) is False


def test_turn_undead_expires_at_one_minute_not_next_cleric_turn() -> None:
    setup, cleric, skeleton, _ = _setup()
    resolve_channel_divinity(
        1, 1, cleric, setup, ChannelDivinityChoice("turn-undead", (skeleton,)), FixedDiceProvider([1]),
    )
    events, sequence = expire_start_of_turn_conditions(2, 10, cleric, setup)
    assert events == [] and sequence == 2
    assert forced_retreat_active(skeleton.state) is True
    events, sequence = expire_start_of_turn_conditions(2, 11, cleric, setup)
    assert sequence == 3
    assert events[0].removed_condition_ids == ["turned-undead", "frightened", "incapacitated"]
    assert skeleton.state.timed_effects == []


def test_divine_spark_damage_uses_wisdom_and_halves_on_success() -> None:
    setup, cleric, skeleton, _ = _setup()
    event, sequence = resolve_channel_divinity(
        1, 1, cleric, setup,
        ChannelDivinityChoice("divine-spark-damage", (skeleton,)),
        FixedDiceProvider([8, 20]),
    )
    assert sequence == 2
    assert event[0].feature_id == "divine-spark"
    assert event[0].save_succeeded is True
    assert event[0].damage_roll.notation == "1d8+3"
    assert event[0].damage_roll.total == 5
    assert _channel_uses(cleric) == 1


def test_divine_spark_heals_another_downed_creature() -> None:
    setup, cleric, _, _ = _setup()
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 5)
    ally.state.current_hp = 0
    ally.state.is_unconscious = True
    setup.heroes.append(ally)
    events, _ = resolve_channel_divinity(
        1, 1, cleric, setup,
        ChannelDivinityChoice("divine-spark-heal", (ally,)),
        FixedDiceProvider([8]),
    )
    assert events[0].healing_roll.total == 11
    assert ally.state.current_hp == 11
    assert ally.state.is_unconscious is False
    assert _channel_uses(cleric) == 1

from app.combat.damage_reaction_events import damage_event_chain
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.zero_hp_rewards import resolve_zero_hp_temporary_hp_reward
from app.content.demo import build_goblin_warrior
from app.content.warlock_fiend_2014_runtime import build_varek_ashenmark_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent


def _setup(level: int = 5):
    warlock = EncounterCombatant(
        combatant_id="varek",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_varek_ashenmark_2014(level)),
    )
    goblin_template = build_goblin_warrior().model_copy(update={"ruleset": "2014"})
    goblin = EncounterCombatant(
        combatant_id="goblin",
        side="monsters",
        position_ft=30,
        state=build_combatant_state(goblin_template),
    )
    setup = EncounterSetup(
        heroes=[warlock],
        monsters=[goblin],
        hero_total_levels=level,
        monster_total_cr="1/4",
        ruleset="2014",
    )
    return warlock, goblin, setup


def _zero_event(source, target, *, hp_before: int = 7, hp_after: int = 0):
    return BattleEvent(
        sequence=1,
        round_number=1,
        event_type="attack",
        actor_id=source.combatant_id,
        actor_name=source.state.template.name,
        target_id=target.combatant_id,
        target_name=target.state.template.name,
        hp_before=hp_before,
        hp_after=hp_after,
        hit=True,
        animation="attack",
        description="test damage",
    )


def test_fiend_zero_hp_reward_is_source_data_and_grants_expected_temporary_hp() -> None:
    source, target, setup = _setup(5)
    grant = source.state.template.progression_features.zero_hp_temporary_hp_grant
    assert grant is not None
    assert grant.source_id == "dark-ones-blessing"
    assert grant.source_name == "Dark One's Blessing"
    assert grant.temporary_hp == 5 + source.state.template.ability_scores.modifier("charisma")

    event = resolve_zero_hp_temporary_hp_reward(2, 1, source, _zero_event(source, target), setup)
    assert event is not None
    assert event.feature_id == "dark-ones-blessing"
    assert event.temporary_hp_before == 0
    assert event.temporary_hp_after == grant.temporary_hp
    assert source.state.temporary_hp == grant.temporary_hp


def test_zero_hp_reward_requires_hostile_crossing_from_positive_hp_to_zero() -> None:
    source, target, setup = _setup(5)
    assert resolve_zero_hp_temporary_hp_reward(
        2, 1, source, _zero_event(source, target, hp_before=0, hp_after=0), setup,
    ) is None
    assert resolve_zero_hp_temporary_hp_reward(
        2, 1, source, _zero_event(source, target, hp_before=7, hp_after=1), setup,
    ) is None

    target.side = "heroes"
    assert resolve_zero_hp_temporary_hp_reward(
        2, 1, source, _zero_event(source, target), setup,
    ) is None


def test_damage_event_chain_emits_zero_hp_reward_before_reaction_dispatch() -> None:
    source, target, setup = _setup(5)
    event = _zero_event(source, target)
    events, sequence = damage_event_chain(
        2, 1, source, event, setup, FixedDiceProvider([1]), turn_key="1:varek",
    )
    assert [item.feature_id for item in events] == [None, "dark-ones-blessing"]
    assert [item.sequence for item in events] == [1, 2]
    assert sequence == 3

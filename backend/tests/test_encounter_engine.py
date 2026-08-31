import app.combat.encounter_engine as encounter_engine
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_engine import run_encounter
from app.combat.encounter_outcome import resolve_encounter_outcome
from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import EncounterSelection


class MaxDiceProvider:
    def roll(self, sides: int) -> int:
        return sides


def test_two_heroes_can_finish_two_monsters_in_shared_turn_loop() -> None:
    result = run_encounter(
        EncounterSelection(
            hero_ids=["aldric-vane-l1", "brom-ironmark-l1"],
            monster_ids=["srd-commoner", "srd-commoner"],
        ),
        MaxDiceProvider(),
    )
    assert result.outcome == "heroes_win"
    assert result.rounds == 1
    assert all(monster.state.current_hp == 0 for monster in result.setup.monsters)
    attack_events = [event for event in result.events if event.event_type == "attack"]
    assert [event.actor_id for event in attack_events] == ["hero-1:aldric-vane-l1", "hero-2:brom-ironmark-l1"]
    assert {event.target_id for event in attack_events} == {"monster-1:srd-commoner", "monster-2:srd-commoner"}


def test_duplicate_monsters_take_distinct_turns_and_retarget_living_heroes() -> None:
    result = run_encounter(
        EncounterSelection(
            hero_ids=["aldric-vane-l1", "brom-ironmark-l1"],
            monster_ids=["srd-goblin-warrior", "srd-goblin-warrior"],
        ),
        MaxDiceProvider(),
    )
    assert result.outcome in {"heroes_win", "monsters_win"}
    goblin_group = next(group for group in result.initiative.groups if group.side == "monsters")
    assert goblin_group.combatant_ids == ["monster-1:srd-goblin-warrior", "monster-2:srd-goblin-warrior"]
    goblin_attacks = [event for event in result.events if event.event_type == "attack" and event.actor_id.startswith("monster-")]
    assert len(goblin_attacks) >= 2
    assert [event.actor_id for event in goblin_attacks[:2]] == goblin_group.combatant_ids
    assert {event.target_id for event in goblin_attacks[:2]} == {"hero-1:aldric-vane-l1", "hero-2:brom-ironmark-l1"}


def _downed_hero_result():
    return run_encounter(
        EncounterSelection(
            hero_ids=["aldric-vane-l1", "brom-ironmark-l1"],
            monster_ids=["srd-goblin-warrior"],
        ),
        FixedDiceProvider([1, 1, 20, 20, 6, 6, 10, 20, 12, 12]),
    )


def test_downed_hero_makes_death_save_while_an_ally_is_still_fighting() -> None:
    result = _downed_hero_result()
    death_save = next(event for event in result.events if event.event_type == "death_save")
    aldric = result.setup.heroes[0].state
    assert death_save.actor_id == "hero-1:aldric-vane-l1"
    assert death_save.death_save_roll is not None
    assert death_save.death_save_roll.total == 10
    assert aldric.current_hp == 0
    assert aldric.is_unconscious is True
    assert aldric.death_save_successes == 1
    assert result.outcome == "heroes_win"


def test_downed_turn_refreshes_reaction_before_death_save(monkeypatch) -> None:
    refreshed_at_zero: list[bool] = []
    original = encounter_engine.refresh_reaction

    def spy(state) -> None:
        if state.current_hp == 0 and not state.is_dead:
            refreshed_at_zero.append(True)
        original(state)

    monkeypatch.setattr(encounter_engine, "refresh_reaction", spy)
    _downed_hero_result()
    assert refreshed_at_zero, "a 0-HP turn must still refresh the creature's Reaction"


def test_zero_hp_character_does_not_end_deathmatch_until_dead() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["aldric-vane-l1"], monster_ids=["srd-commoner"],
    ))
    hero = setup.heroes[0].state
    hero.current_hp = 0
    hero.is_unconscious = True
    assert resolve_encounter_outcome(setup) == "active"
    hero.is_dead = True
    hero.is_alive = False
    hero.is_unconscious = False
    assert resolve_encounter_outcome(setup) == "monsters_win"


def test_ranged_attacker_fires_while_closing_instead_of_holding_range() -> None:
    result = run_encounter(
        EncounterSelection(
            hero_ids=["selene-asharrow-l1"],
            monster_ids=["srd-commoner"],
        ),
        MaxDiceProvider(),
    )
    assert result.outcome == "heroes_win"
    attack = next(event for event in result.events if event.event_type == "attack")
    movement = next(event for event in result.events if event.event_type == "movement" and event.actor_id == "hero-1:selene-asharrow-l1")
    assert attack.actor_id == "hero-1:selene-asharrow-l1"
    assert attack.target_id == "monster-1:srd-commoner"
    assert movement.distance_after_ft < movement.distance_before_ft

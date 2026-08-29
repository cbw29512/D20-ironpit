from app.combat.encounter_engine import run_encounter
from app.domain.models import EncounterSelection


class MaxDiceProvider:
    def roll(self, sides: int) -> int:
        return sides


def test_two_heroes_can_finish_two_monsters_in_shared_turn_loop() -> None:
    result = run_encounter(
        EncounterSelection(
            hero_ids=["aldric-vane-l1", "brom-ironmark-l1"],
            monster_ids=["srd-commoner", "srd-commoner"],
            starting_distance_ft=30,
        ),
        MaxDiceProvider(),
    )

    assert result.outcome == "heroes_win"
    assert result.rounds == 1
    assert all(monster.state.current_hp == 0 for monster in result.setup.monsters)
    attack_events = [event for event in result.events if event.event_type == "attack"]
    assert [event.actor_id for event in attack_events] == [
        "hero-1:aldric-vane-l1",
        "hero-2:brom-ironmark-l1",
    ]
    assert {event.target_id for event in attack_events} == {
        "monster-1:srd-commoner",
        "monster-2:srd-commoner",
    }


def test_duplicate_monsters_take_distinct_turns_and_retarget_living_heroes() -> None:
    result = run_encounter(
        EncounterSelection(
            hero_ids=["aldric-vane-l1", "brom-ironmark-l1"],
            monster_ids=["srd-goblin-warrior", "srd-goblin-warrior"],
            starting_distance_ft=30,
        ),
        MaxDiceProvider(),
    )

    assert result.outcome == "monsters_win"
    goblin_group = next(group for group in result.initiative.groups if group.side == "monsters")
    assert goblin_group.combatant_ids == [
        "monster-1:srd-goblin-warrior",
        "monster-2:srd-goblin-warrior",
    ]
    attacks = [event for event in result.events if event.event_type == "attack"]
    assert [event.actor_id for event in attacks[:2]] == goblin_group.combatant_ids
    assert [event.target_id for event in attacks[:2]] == [
        "hero-1:aldric-vane-l1",
        "hero-2:brom-ironmark-l1",
    ]


def test_ranged_attacker_does_not_kite_or_close_when_already_in_normal_range() -> None:
    result = run_encounter(
        EncounterSelection(
            hero_ids=["selene-asharrow-l1"],
            monster_ids=["srd-commoner"],
            starting_distance_ft=90,
        ),
        MaxDiceProvider(),
    )

    assert result.outcome == "heroes_win"
    assert not any(
        event.event_type == "movement" and event.actor_id == "hero-1:selene-asharrow-l1"
        for event in result.events
    )
    attack = next(event for event in result.events if event.event_type == "attack")
    assert attack.actor_id == "hero-1:selene-asharrow-l1"
    assert attack.target_id == "monster-1:srd-commoner"

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_events import build_initiative_events
from app.combat.encounter_initiative import roll_encounter_initiative
from app.combat.encounter_outcome import resolve_encounter_outcome
from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import EncounterSelection


def _setup(heroes: list[str], monsters: list[str]):
    return build_encounter_setup(EncounterSelection(hero_ids=heroes, monster_ids=monsters))


def test_identical_monsters_share_one_raw_initiative_roll() -> None:
    setup = _setup(["karnok-stoneward-l1"], ["srd-goblin-warrior", "srd-goblin-warrior"])
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([10, 15]))

    goblins = initiative.groups[0]
    assert goblins.template_id == "srd-goblin-warrior"
    assert goblins.combatant_ids == [
        "monster-1:srd-goblin-warrior",
        "monster-2:srd-goblin-warrior",
    ]
    assert setup.monsters[0].state.initiative_roll == 15
    assert setup.monsters[1].state.initiative_roll == 15
    assert initiative.turn_order[:2] == goblins.combatant_ids


def test_initiative_event_preserves_full_advantage_roll_provenance() -> None:
    setup = _setup(["karnok-stoneward-l3"], ["srd-commoner"])
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([7, 18, 10]))

    fighter = next(group for group in initiative.groups if group.side == "heroes")
    assert fighter.initiative_roll.mode == "advantage"
    assert fighter.initiative_roll.notation == "2d20"
    assert fighter.initiative_roll.rolls == [7, 18]
    assert fighter.initiative_roll.selected_roll == 18
    assert fighter.initiative_roll.modifier == 1
    assert fighter.initiative_roll.total == 19

    events, next_sequence = build_initiative_events(initiative, 1)
    fighter_event = next(event for event in events if event.actor_id.startswith("hero-1:"))
    assert fighter_event.attack_roll == fighter.initiative_roll
    assert fighter_event.attack_roll is not None
    assert fighter_event.attack_roll.rolls == [7, 18]
    assert next_sequence == 3


def test_tied_heroes_keep_selected_party_order() -> None:
    setup = _setup(["karnok-stoneward-l1", "rokhan-stonefury-l1"], ["srd-commoner"])
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([10, 10, 1]))

    assert initiative.turn_order[:2] == [
        "hero-1:karnok-stoneward-l1",
        "hero-2:rokhan-stonefury-l1",
    ]


def test_cross_side_tie_uses_explicit_arena_gm_tiebreak() -> None:
    setup = _setup(["karnok-stoneward-l1"], ["srd-commoner"])
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([10, 11, 17]))

    assert initiative.groups[0].side == "heroes"
    assert initiative.groups[0].tie_break_roll == 17
    assert initiative.groups[1].side == "monsters"
    assert initiative.groups[1].tie_break_roll == 4


def test_encounter_outcome_requires_an_entire_side_down() -> None:
    setup = _setup(
        ["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        ["srd-commoner", "srd-bandit"],
    )
    assert resolve_encounter_outcome(setup) == "active"

    setup.monsters[0].state.current_hp = 0
    setup.monsters[0].state.is_alive = False
    assert resolve_encounter_outcome(setup) == "active"

    setup.monsters[1].state.current_hp = 0
    setup.monsters[1].state.is_alive = False
    assert resolve_encounter_outcome(setup) == "heroes_win"


def test_simultaneous_side_defeat_is_a_draw() -> None:
    setup = _setup(["karnok-stoneward-l1"], ["srd-commoner"])
    setup.heroes[0].state.current_hp = 0
    setup.heroes[0].state.is_alive = False
    setup.monsters[0].state.current_hp = 0
    setup.monsters[0].state.is_alive = False
    assert resolve_encounter_outcome(setup) == "draw"

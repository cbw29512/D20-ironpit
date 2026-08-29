from app.combat.dice import FixedDiceProvider
from app.combat.encounter_initiative import roll_encounter_initiative
from app.combat.encounter_outcome import resolve_encounter_outcome
from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import EncounterSelection


def _setup(heroes: list[str], monsters: list[str]):
    return build_encounter_setup(EncounterSelection(hero_ids=heroes, monster_ids=monsters))


def test_identical_monsters_share_one_raw_initiative_roll() -> None:
    setup = _setup(["aldric-vane-l1"], ["srd-goblin-warrior", "srd-goblin-warrior"])
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


def test_tied_heroes_keep_selected_party_order() -> None:
    setup = _setup(["aldric-vane-l1", "brom-ironmark-l1"], ["srd-commoner"])
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([10, 10, 1]))

    assert initiative.turn_order[:2] == [
        "hero-1:aldric-vane-l1",
        "hero-2:brom-ironmark-l1",
    ]


def test_cross_side_tie_uses_explicit_arena_gm_tiebreak() -> None:
    setup = _setup(["aldric-vane-l1"], ["srd-commoner"])
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([10, 11, 17]))

    assert initiative.groups[0].side == "heroes"
    assert initiative.groups[0].tie_break_roll == 17
    assert initiative.groups[1].side == "monsters"
    assert initiative.groups[1].tie_break_roll == 4


def test_encounter_outcome_requires_an_entire_side_down() -> None:
    setup = _setup(["aldric-vane-l1", "mara-quickstep-l1"], ["srd-commoner", "srd-bandit"])
    assert resolve_encounter_outcome(setup) == "active"

    setup.monsters[0].state.current_hp = 0
    setup.monsters[0].state.is_alive = False
    assert resolve_encounter_outcome(setup) == "active"

    setup.monsters[1].state.current_hp = 0
    setup.monsters[1].state.is_alive = False
    assert resolve_encounter_outcome(setup) == "heroes_win"


def test_simultaneous_side_defeat_is_a_draw() -> None:
    setup = _setup(["aldric-vane-l1"], ["srd-commoner"])
    setup.heroes[0].state.current_hp = 0
    setup.heroes[0].state.is_alive = False
    setup.monsters[0].state.current_hp = 0
    setup.monsters[0].state.is_alive = False
    assert resolve_encounter_outcome(setup) == "draw"

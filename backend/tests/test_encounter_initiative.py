from app.combat.dice import FixedDiceProvider
from app.combat.encounter_events import build_initiative_events
from app.combat.encounter_initiative import roll_encounter_initiative
from app.combat.encounter_outcome import resolve_encounter_outcome
from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import EncounterSelection
from app.domain.modifiers import CombatModifier, ModifierKind


def _setup(heroes: list[str], monsters: list[str]):
    return build_encounter_setup(EncounterSelection(hero_ids=heroes, monster_ids=monsters))


def _neutralize_initiative(setup) -> None:
    for member in [*setup.heroes, *setup.monsters]:
        member.state.template.initiative_bonus = 0
        member.state.template.progression_features.initiative_advantage = False


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



def test_universal_d20_test_advantage_applies_to_initiative() -> None:
    setup = _setup(["karnok-stoneward-l1"], ["srd-commoner"])
    _neutralize_initiative(setup)
    hero = setup.heroes[0].state
    hero.active_modifiers.append(CombatModifier(
        id="hero:foresight:d20",
        source_id=setup.heroes[0].combatant_id,
        source_effect_id="foresight",
        source_name="Foresight",
        kind=ModifierKind.D20_TEST_ADVANTAGE,
    ))

    initiative = roll_encounter_initiative(setup, FixedDiceProvider([2, 17, 10]))
    hero_group = next(group for group in initiative.groups if group.side == "heroes")

    assert hero_group.initiative_roll.mode == "advantage"
    assert hero_group.initiative_roll.rolls == [2, 17]
    assert hero_group.initiative_roll.selected_roll == 17

def test_natural_20_is_only_the_check_total() -> None:
    setup = _setup(["karnok-stoneward-l1"], ["srd-commoner"])
    _neutralize_initiative(setup)
    setup.monsters[0].state.template.initiative_bonus = 2
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([20, 19]))

    assert initiative.groups[0].side == "monsters"
    assert initiative.groups[0].initiative_count == 21
    assert initiative.groups[1].side == "heroes"
    assert initiative.groups[1].natural_roll == 20
    assert initiative.groups[1].initiative_count == 20
    events, _ = build_initiative_events(initiative, 1)
    assert all("top initiative priority" not in event.description for event in events)
    assert all("Tie reroll" not in event.description for event in events)


def test_natural_1_has_bottom_priority() -> None:
    setup = _setup(["karnok-stoneward-l1"], ["srd-commoner"])
    _neutralize_initiative(setup)
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([1, 2]))

    assert initiative.groups[-1].side == "heroes"
    assert initiative.groups[-1].natural_roll == 1
    events, _ = build_initiative_events(initiative, 1)
    hero_event = next(event for event in events if event.actor_id.startswith("hero-1:"))
    assert "Natural 1: bottom initiative priority." in hero_event.description


def test_pc_monster_tie_uses_dm_decision_without_reroll() -> None:
    setup = _setup(["karnok-stoneward-l1"], ["srd-commoner"])
    _neutralize_initiative(setup)
    leftover = FixedDiceProvider([14, 14, 3])
    initiative = roll_encounter_initiative(setup, leftover)

    hero = next(group for group in initiative.groups if group.side == "heroes")
    monster = next(group for group in initiative.groups if group.side == "monsters")
    assert hero.initiative_count == 14
    assert monster.initiative_count == 14
    assert hero.tie_break_rolls == []
    assert monster.tie_break_rolls == []
    assert monster.tie_break_roll is None
    assert initiative.groups[0].side == "heroes"
    leftover.roll(20)

    events, _ = build_initiative_events(initiative, 1)
    assert any("Tied initiative: DM decides; heroes act before monsters, then encounter order." in event.description for event in events)
    assert all("Tie reroll" not in event.description for event in events)


def test_pc_pc_tie_uses_party_order_without_reroll() -> None:
    setup = _setup(["karnok-stoneward-l1", "rokhan-stonefury-l1"], ["srd-commoner"])
    _neutralize_initiative(setup)
    leftover = FixedDiceProvider([14, 14, 5, 3])
    initiative = roll_encounter_initiative(setup, leftover)

    assert initiative.turn_order[:2] == [
        setup.heroes[0].combatant_id,
        setup.heroes[1].combatant_id,
    ]
    assert all(group.tie_break_rolls == [] for group in initiative.groups)
    leftover.roll(20)

    events, _ = build_initiative_events(initiative, 1)
    hero_events = [event for event in events if event.actor_id.startswith("hero-")]
    assert any("Tied initiative: players decide; party order." in event.description for event in hero_events)
    assert all("Tie reroll" not in event.description for event in events)


def test_monster_monster_tie_uses_encounter_order_without_reroll() -> None:
    setup = _setup(["karnok-stoneward-l1"], ["srd-commoner", "srd-bandit"])
    _neutralize_initiative(setup)
    leftover = FixedDiceProvider([3, 11, 11, 4])
    initiative = roll_encounter_initiative(setup, leftover)

    assert initiative.turn_order == [
        setup.monsters[0].combatant_id,
        setup.monsters[1].combatant_id,
        setup.heroes[0].combatant_id,
    ]
    assert all(group.tie_break_rolls == [] for group in initiative.groups)
    leftover.roll(20)

    events, _ = build_initiative_events(initiative, 1)
    monster_events = [event for event in events if event.actor_id.startswith("monster-")]
    assert any("Tied initiative: DM decides; encounter order." in event.description for event in monster_events)
    assert all("Tie reroll" not in event.description for event in events)


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

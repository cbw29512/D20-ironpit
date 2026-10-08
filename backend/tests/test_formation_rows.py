from app.combat.encounter_setup import build_encounter_setup
from app.combat.formation_rows import member_is_backline, sync_formation_rows
from app.combat.offensive_movement_policy import choose_offensive_movement_intent
from app.combat.state import begin_turn
from app.domain.models import EncounterSelection


def test_mixed_melee_and_ranged_cards_split_front_and_back() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["rokhan-stonefury-2014-l3"],
        monster_ids=["2014-goblin", "2014-goblin"],
        ruleset="2014",
    ))
    front, back = setup.monsters
    assert front.state.formation_row == "front"
    assert back.state.formation_row == "back"
    assert member_is_backline(front) is False
    assert member_is_backline(back) is True
    assert setup.heroes[0].state.formation_row == "front"


def test_melee_only_back_row_steps_up_when_front_ally_dies() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-2014-l1", "rokhan-stonefury-2014-l1"],
        monster_ids=["2014-goblin"],
        ruleset="2014",
    ))
    melee = setup.heroes[1]
    melee.state.template.alternate_weapon_attacks = []
    melee.state.formation_row = "back"
    melee.state.initial_formation_row = "back"
    setup.heroes[0].state.current_hp = 0
    setup.heroes[0].state.is_alive = False
    setup.heroes[0].state.is_dead = True

    promoted = sync_formation_rows(setup)
    assert [item.combatant_id for item in promoted] == [melee.combatant_id]
    assert melee.state.formation_row == "front"


def test_back_row_with_ranged_attack_steps_up_when_last_front_falls() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["rokhan-stonefury-2014-l3"],
        monster_ids=["2014-goblin", "2014-goblin"],
        ruleset="2014",
    ))
    setup.monsters[0].state.current_hp = 0
    setup.monsters[0].state.is_alive = False
    setup.monsters[0].state.is_dead = True

    assert [member.combatant_id for member in sync_formation_rows(setup)] == [setup.monsters[1].combatant_id]
    assert setup.monsters[1].state.formation_row == "front"
    assert setup.monsters[1].state.initial_formation_row == "back"


def test_front_row_melee_plans_closing_when_backup_range_already_lands() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["rokhan-stonefury-2014-l3"],
        monster_ids=["2014-goblin", "2014-goblin"],
        ruleset="2014",
    ))
    barbarian = setup.heroes[0]
    begin_turn(barbarian.state)
    intent = choose_offensive_movement_intent(barbarian, setup, "1:hero")
    assert intent is not None
    assert intent.family == "melee"
    assert intent.target_id == setup.monsters[0].combatant_id

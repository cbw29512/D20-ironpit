from app.combat.encounter_setup import build_encounter_setup
from app.combat.formation_rows import assign_formation_rows, member_is_backline, sync_formation_rows
from app.combat.state import build_combatant_state
from app.content.pregens import build_selene_asharrow
from app.domain.encounters import EncounterCombatant
from app.combat.offensive_movement_policy import choose_offensive_movement_intent
from app.combat.state import begin_turn
from app.domain.models import EncounterSelection


def test_two_mixed_attack_cards_start_in_front_when_below_three_slots() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["rokhan-stonefury-2014-l3"],
        monster_ids=["2014-goblin", "2014-goblin"],
        ruleset="2014",
    ))
    front, back = setup.monsters
    assert front.state.formation_row == "front"
    assert back.state.formation_row == "front"
    assert member_is_backline(front) is False
    assert member_is_backline(back) is False
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
        monster_ids=["2014-goblin"] * 4,
        ruleset="2014",
    ))
    assert [member.state.formation_row for member in setup.monsters] == ["front", "front", "front", "back"]
    for front in setup.monsters[:3]:
        front.state.current_hp = 0
        front.state.is_alive = False
        front.state.is_dead = True

    assert [member.combatant_id for member in sync_formation_rows(setup)] == [setup.monsters[3].combatant_id]
    assert setup.monsters[3].state.formation_row == "front"
    assert setup.monsters[3].state.initial_formation_row == "back"


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


def test_single_ranged_specialist_prefers_back_slot_with_real_coordinates() -> None:
    selene = build_selene_asharrow()
    member = EncounterCombatant(
        combatant_id="hero-ranged-fixture", side="heroes", position_ft=0,
        state=build_combatant_state(selene),
    )
    assign_formation_rows([member])
    assert member.state.initial_formation_row == "back"
    assert member.state.formation_row == "back"


def test_six_ranged_specialists_fill_three_back_then_three_front_slots() -> None:
    selene = build_selene_asharrow()
    members = [
        EncounterCombatant(
            combatant_id=f"hero-ranged-{i}", side="heroes", position_ft=0,
            state=build_combatant_state(selene),
        )
        for i in range(6)
    ]
    assign_formation_rows(members)
    assert [m.state.formation_row for m in members] == [
        "back", "back", "back", "front", "front", "front",
    ]

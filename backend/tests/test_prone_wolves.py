from app.combat.ally_context import pack_tactics_active
from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monsters_wolves import build_dire_wolf, build_wolf
from app.domain.models import EncounterSelection, RollMode


def test_wolf_bite_knocks_medium_target_prone_on_hit() -> None:
    wolf = build_combatant_state(build_wolf())
    target = build_combatant_state(build_karnok_stoneward())

    event = resolve_attack(1, 1, wolf, target, wolf.template.weapon_attack, 5, FixedDiceProvider([15, 3]))

    assert event.hit is True
    assert event.damage_roll is not None
    assert event.damage_roll.total == 5
    assert event.applied_condition_ids == ["prone"]
    assert "prone" in target.active_effect_ids


def test_wolf_bite_does_not_knock_large_target_prone() -> None:
    wolf = build_combatant_state(build_wolf())
    target = build_combatant_state(build_dire_wolf())

    event = resolve_attack(1, 1, wolf, target, wolf.template.weapon_attack, 5, FixedDiceProvider([15, 3]))

    assert event.hit is True
    assert event.applied_condition_ids == []
    assert "prone" not in target.active_effect_ids


def test_dire_wolf_bite_can_knock_large_target_prone() -> None:
    wolf = build_combatant_state(build_dire_wolf())
    target = build_combatant_state(build_dire_wolf())

    event = resolve_attack(1, 1, wolf, target, wolf.template.weapon_attack, 5, FixedDiceProvider([15, 5]))

    assert event.hit is True
    assert event.damage_roll is not None
    assert event.damage_roll.total == 8
    assert event.applied_condition_ids == ["prone"]


def test_prone_attacker_has_disadvantage() -> None:
    attacker = build_combatant_state(build_karnok_stoneward())
    defender = build_combatant_state(build_wolf())
    attacker.active_effect_ids.append("prone")

    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5, FixedDiceProvider([15, 2])
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.attack_roll.selected_roll == 2


def test_attack_within_five_feet_of_prone_target_has_advantage() -> None:
    attacker = build_combatant_state(build_wolf())
    defender = build_combatant_state(build_karnok_stoneward())
    defender.active_effect_ids.append("prone")

    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5, FixedDiceProvider([2, 15, 3])
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.selected_roll == 15


def test_prone_combatant_spends_half_speed_to_stand_at_turn_start() -> None:
    state = build_combatant_state(build_karnok_stoneward())
    state.active_effect_ids.append("prone")

    begin_turn(state)

    assert "prone" not in state.active_effect_ids
    assert state.movement_remaining_ft == 15


def test_two_wolves_activate_pack_tactics_under_arena_adjacency() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=["srd-wolf", "srd-wolf"],
        starting_distance_ft=5,
    ))
    wolf = setup.monsters[0]
    target = setup.heroes[0]

    assert pack_tactics_active(wolf, target, setup) is True


def test_single_wolf_does_not_activate_pack_tactics() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=["srd-wolf"],
        starting_distance_ft=5,
    ))

    assert pack_tactics_active(setup.monsters[0], setup.heroes[0], setup) is False

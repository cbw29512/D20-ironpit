from app.combat.attacks import resolve_attack
from app.combat.conditions import attack_roll_condition_sources
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import select_nearest_target
from app.combat.grapple import (
    apply_grapple,
    cleanup_grapples,
    resolve_escape_grapple,
    speed_is_zero,
)
from app.domain.models import EncounterSelection, RollMode


def _setup(monster_ids=None):
    return build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=monster_ids or ["srd-crocodile"],
        starting_distance_ft=5,
    ))


def test_crocodile_bite_applies_grapple_restrained_and_ends_dodge() -> None:
    setup = _setup()
    hero, crocodile = setup.heroes[0], setup.monsters[0]
    hero.state.active_effect_ids.append("dodge")

    event = resolve_attack(
        1, 1, crocodile.state, hero.state, crocodile.state.template.weapon_attack, 5,
        FixedDiceProvider([15, 15, 1]),
        actor_event_id=crocodile.combatant_id,
        target_event_id=hero.combatant_id,
    )

    assert event.hit is True
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.applied_condition_ids == ["grappled", "restrained"]
    assert set(hero.state.active_effect_ids) >= {"grappled", "restrained"}
    assert "dodge" not in hero.state.active_effect_ids
    assert speed_is_zero(hero.state) is True
    assert hero.state.grapple_sources[0].source_id == crocodile.combatant_id
    assert hero.state.grapple_sources[0].escape_dc == 12


def test_grappled_attacker_only_has_disadvantage_against_non_grappler() -> None:
    setup = _setup(["srd-giant-crab", "srd-commoner"])
    hero, crab, commoner = setup.heroes[0], *setup.monsters
    apply_grapple(hero.state, crab.combatant_id, 11, 5)

    _, versus_grappler = attack_roll_condition_sources(
        hero.state, crab.state, 5, crab.combatant_id,
    )
    _, versus_other = attack_roll_condition_sources(
        hero.state, commoner.state, 5, commoner.combatant_id,
    )

    assert versus_grappler == 0
    assert versus_other == 1
    assert select_nearest_target(hero, setup).combatant_id == crab.combatant_id


def test_grappler_keeps_attacking_a_held_target() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        monster_ids=["srd-giant-crab"],
        starting_distance_ft=5,
    ))
    crab = setup.monsters[0]
    held, other = setup.heroes
    apply_grapple(held.state, crab.combatant_id, 11, 5)
    other.position_ft = crab.position_ft

    assert select_nearest_target(crab, setup).combatant_id == held.combatant_id


def test_grapple_ends_when_grappler_is_dead_or_out_of_range() -> None:
    setup = _setup()
    hero, crocodile = setup.heroes[0], setup.monsters[0]
    apply_grapple(hero.state, crocodile.combatant_id, 12, 5, restrains=True)
    crocodile.state.is_dead = True
    crocodile.state.is_alive = False

    cleanup_grapples(setup)
    assert hero.state.grapple_sources == []
    assert "grappled" not in hero.state.active_effect_ids
    assert "restrained" not in hero.state.active_effect_ids

    crocodile.state.is_dead = False
    crocodile.state.is_alive = True
    apply_grapple(hero.state, crocodile.combatant_id, 12, 5, restrains=True)
    crocodile.position_ft = 30
    cleanup_grapples(setup)
    assert hero.state.grapple_sources == []


def test_restrained_grapple_escape_spends_action_and_rage_helps_strength_check() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["rokhan-stonefury-l1"], monster_ids=["srd-crocodile"], starting_distance_ft=5,
    ))
    hero, crocodile = setup.heroes[0], setup.monsters[0]
    hero.state.action_available = True
    hero.state.movement_remaining_ft = 0
    hero.state.active_effect_ids.append("rage")
    apply_grapple(hero.state, crocodile.combatant_id, 12, 5, restrains=True)

    event = resolve_escape_grapple(
        1, 1, hero.combatant_id, hero.state, FixedDiceProvider([1, 7]),
    )

    assert event.ability_check_roll is not None
    assert event.ability_check_roll.mode is RollMode.ADVANTAGE
    assert event.ability_check_roll.selected_roll == 7
    assert event.check_succeeded is True
    assert hero.state.action_available is False
    assert hero.state.grapple_sources == []
    assert hero.state.movement_remaining_ft == hero.state.template.speed_ft

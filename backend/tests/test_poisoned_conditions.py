from app.combat.attacks import resolve_attack
from app.combat.conditions import attack_roll_condition_sources
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.grapple import apply_grapple, resolve_escape_grapple
from app.combat.timed_conditions import expire_start_of_turn_conditions
from app.domain.models import EncounterSelection, RollMode


def _setup():
    return build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=["srd-giant-centipede"],
        starting_distance_ft=5,
    ))


def test_giant_centipede_matches_srd_5_2_1_profile() -> None:
    setup = _setup()
    centipede = setup.monsters[0].state.template
    attack = centipede.weapon_attack

    assert (centipede.challenge_rating, centipede.size.value) == ("1/4", "small")
    assert (centipede.armor_class, centipede.max_hp, centipede.speed_ft, centipede.initiative_bonus) == (14, 9, 30, 2)
    assert (attack.attack_bonus, attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus) == (4, 1, 4, 2)
    assert attack.control_effect is not None
    assert attack.control_effect.condition_id == "poisoned"
    assert attack.control_effect.expires_at_start_of_source_turn is True


def test_centipede_bite_applies_timed_poisoned_condition() -> None:
    setup = _setup()
    hero, centipede = setup.heroes[0], setup.monsters[0]

    event = resolve_attack(
        1, 1, centipede.state, hero.state, centipede.state.template.weapon_attack, 5,
        FixedDiceProvider([15, 1]),
        actor_event_id=centipede.combatant_id,
        target_event_id=hero.combatant_id,
    )

    assert event.hit is True
    assert event.applied_condition_ids == ["poisoned"]
    assert "poisoned" in hero.state.active_effect_ids
    assert len(hero.state.timed_effects) == 1
    assert hero.state.timed_effects[0].source_id == centipede.combatant_id


def test_poisoned_gives_attack_roll_disadvantage() -> None:
    setup = _setup()
    hero, centipede = setup.heroes[0], setup.monsters[0]
    hero.state.active_effect_ids.append("poisoned")

    advantage, disadvantage = attack_roll_condition_sources(
        hero.state, centipede.state, 5, centipede.combatant_id,
    )
    assert advantage == 0
    assert disadvantage == 1


def test_poisoned_gives_grapple_escape_check_disadvantage() -> None:
    setup = _setup()
    hero, centipede = setup.heroes[0], setup.monsters[0]
    hero.state.active_effect_ids.append("poisoned")
    apply_grapple(hero.state, centipede.combatant_id, 12, 5, restrains=True)

    event = resolve_escape_grapple(
        1, 1, hero.combatant_id, hero.state, FixedDiceProvider([18, 2]),
    )

    assert event.ability_check_roll is not None
    assert event.ability_check_roll.mode is RollMode.DISADVANTAGE
    assert event.ability_check_roll.selected_roll == 2


def test_timed_poison_expires_at_source_slot_even_if_source_died() -> None:
    setup = _setup()
    hero, centipede = setup.heroes[0], setup.monsters[0]
    resolve_attack(
        1, 1, centipede.state, hero.state, centipede.state.template.weapon_attack, 5,
        FixedDiceProvider([15, 1]),
        actor_event_id=centipede.combatant_id,
        target_event_id=hero.combatant_id,
    )
    centipede.state.current_hp = 0
    centipede.state.is_alive = False
    centipede.state.is_dead = True

    events, sequence = expire_start_of_turn_conditions(2, 2, centipede, setup)

    assert sequence == 3
    assert len(events) == 1
    assert events[0].removed_condition_ids == ["poisoned"]
    assert events[0].target_id == hero.combatant_id
    assert "poisoned" not in hero.state.active_effect_ids
    assert hero.state.timed_effects == []

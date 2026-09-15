from app.combat.attacks import resolve_attack
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.conditions import attack_roll_condition_sources
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.grapple import apply_grapple, resolve_escape_grapple
from app.combat.timed_conditions import apply_timed_condition
from app.domain.models import EncounterSelection, RollMode


def _setup(monster_ids=None):
    return build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=monster_ids or ["srd-giant-centipede"],
    ))


def test_giant_centipede_preserves_exact_srd_poison_source_profile() -> None:
    centipede = _setup().monsters[0].state.template
    attack = centipede.weapon_attack
    assert (centipede.challenge_rating, centipede.size.value) == ("1/4", "small")
    assert (centipede.armor_class, centipede.max_hp, centipede.speed_ft, centipede.initiative_bonus) == (14, 9, 30, 2)
    assert (attack.attack_bonus, attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus) == (4, 1, 4, 2)
    assert attack.control_effect is not None
    assert attack.control_effect.condition_id == "poisoned"
    assert attack.control_effect.expiry_timing == "source_turn_start"
    assert attack.control_effect.expires_at_start_of_source_turn is True
    assert attack.control_effect.repeat_save_ability is None


def test_poison_hit_keeps_source_expiry_and_does_not_invent_recovery_save() -> None:
    setup = _setup()
    hero, centipede = setup.heroes[0], setup.monsters[0]
    event = resolve_attack(
        1, 1, centipede.state, hero.state, centipede.state.template.weapon_attack, 5,
        FixedDiceProvider([15, 1]), actor_event_id=centipede.combatant_id, target_event_id=hero.combatant_id,
    )
    assert event.hit is True
    assert event.applied_condition_ids == ["poisoned"]
    assert len(hero.state.timed_effects) == 1
    poison = hero.state.timed_effects[0]
    assert poison.effect_id == "poisoned"
    assert poison.expiry_timing == "source_turn_start"
    assert poison.expires_at_start_of_source_turn is True
    assert poison.repeat_save_ability is None
    assert poison.repeat_save_dc is None
    assert poison.repeat_save_timing is None


def test_poisoned_gives_attack_and_escape_check_disadvantage() -> None:
    setup = _setup()
    hero, centipede = setup.heroes[0], setup.monsters[0]
    hero.state.active_effect_ids.append("poisoned")
    advantage, disadvantage = attack_roll_condition_sources(hero.state, centipede.state, 5, centipede.combatant_id)
    assert advantage == 0 and disadvantage == 1
    apply_grapple(hero.state, centipede.combatant_id, 12, 5, restrains=True)
    event = resolve_escape_grapple(1, 1, hero.combatant_id, hero.state, FixedDiceProvider([18, 2]))
    assert event.ability_check_roll is not None
    assert event.ability_check_roll.mode is RollMode.DISADVANTAGE
    assert event.ability_check_roll.selected_roll == 2


def test_poison_does_not_stack_across_sources() -> None:
    setup = _setup(["srd-giant-centipede", "srd-giant-centipede"])
    hero, first, second = setup.heroes[0], *setup.monsters
    assert apply_timed_condition(hero.state, "poisoned", first.combatant_id) == "poisoned"
    assert apply_timed_condition(hero.state, "poisoned", second.combatant_id) == "poisoned"
    assert hero.state.active_effect_ids.count("poisoned") == 1
    assert len([effect for effect in hero.state.timed_effects if effect.effect_id == "poisoned"]) == 1


def test_protection_from_poison_blocks_poisoned_condition() -> None:
    setup = _setup()
    hero, centipede = setup.heroes[0], setup.monsters[0]
    hero.state.active_buff_effect_ids.append("protection-from-poison")
    assert apply_timed_condition(hero.state, "poisoned", centipede.combatant_id) is None
    assert "poisoned" not in hero.state.active_effect_ids


def test_explicit_repeat_save_delay_is_condition_neutral() -> None:
    setup = _setup()
    hero, centipede = setup.heroes[0], setup.monsters[0]
    apply_timed_condition(
        hero.state,
        "frightened",
        centipede.combatant_id,
        source_effect_id="test-fear",
        applied_round=1,
        expires_at_start_of_source_turn=False,
        repeat_save_ability="constitution",
        repeat_save_dc=10,
        repeat_save_timing="target_turn_start",
        repeat_save_delay_rounds=1,
    )

    same_round, sequence = resolve_target_condition_timing(1, 1, hero, "target_turn_start", FixedDiceProvider([20]))
    assert same_round == [] and sequence == 1
    failed, sequence = resolve_target_condition_timing(sequence, 2, hero, "target_turn_start", FixedDiceProvider([1]))
    assert failed[0].save_succeeded is False and "frightened" in hero.state.active_effect_ids
    succeeded, sequence = resolve_target_condition_timing(sequence, 3, hero, "target_turn_start", FixedDiceProvider([20]))
    assert succeeded[0].save_succeeded is True
    assert succeeded[0].removed_condition_ids == ["frightened"]
    assert "frightened" not in hero.state.active_effect_ids

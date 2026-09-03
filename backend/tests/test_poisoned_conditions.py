from app.combat.attacks import resolve_attack
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.conditions import attack_roll_condition_sources
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.grapple import apply_grapple, resolve_escape_grapple
from app.combat.timed_conditions import ARENA_POISON_RECOVERY_DC, apply_timed_condition
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
    assert attack.control_effect.expires_at_start_of_source_turn is True


def test_poison_hit_normalizes_to_one_arena_recovery_effect() -> None:
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
    assert poison.expiry_timing is None
    assert poison.expires_at_start_of_source_turn is False
    assert (poison.repeat_save_ability, poison.repeat_save_dc, poison.repeat_save_timing) == (
        "constitution", ARENA_POISON_RECOVERY_DC, "target_turn_start",
    )


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


def test_protection_from_poison_blocks_arena_poison() -> None:
    setup = _setup()
    hero, centipede = setup.heroes[0], setup.monsters[0]
    hero.state.active_buff_effect_ids.append("protection-from-poison")
    assert apply_timed_condition(hero.state, "poisoned", centipede.combatant_id) is None
    assert "poisoned" not in hero.state.active_effect_ids


def test_poison_recovery_repeats_at_target_turn_start_until_success() -> None:
    setup = _setup()
    hero, centipede = setup.heroes[0], setup.monsters[0]
    apply_timed_condition(hero.state, "poisoned", centipede.combatant_id)

    failed, sequence = resolve_target_condition_timing(1, 2, hero, "target_turn_start", FixedDiceProvider([1]))
    assert sequence == 2
    assert failed[0].save_succeeded is False
    assert "poisoned" in hero.state.active_effect_ids

    succeeded, sequence = resolve_target_condition_timing(sequence, 3, hero, "target_turn_start", FixedDiceProvider([20]))
    assert sequence == 3
    assert succeeded[0].save_succeeded is True
    assert succeeded[0].removed_condition_ids == ["poisoned"]
    assert "poisoned" not in hero.state.active_effect_ids
    assert hero.state.timed_effects == []

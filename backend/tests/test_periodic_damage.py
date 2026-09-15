from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.timed_conditions import apply_timed_condition
from app.domain.models import DamageType, EncounterSelection
from app.domain.save_effects import PeriodicDamageEffectDefinition


def _setup():
    return build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-vrock"],
    ))


def _periodic_poison() -> PeriodicDamageEffectDefinition:
    return PeriodicDamageEffectDefinition(
        timing="target_turn_start", dice_count=1, dice_size=10,
        damage_bonus=0, damage_type=DamageType.POISON,
    )


def test_periodic_damage_ticks_then_repeat_save_ends_effect() -> None:
    setup = _setup()
    hero, vrock = setup.heroes[0], setup.monsters[0]
    hp_before = hero.state.current_hp
    apply_timed_condition(
        hero.state, "poisoned", vrock.combatant_id,
        source_effect_id="spores", applied_round=1,
        repeat_save_ability="constitution", repeat_save_dc=14,
        repeat_save_timing="target_turn_end", periodic_damage=_periodic_poison(),
    )

    ticks, sequence = resolve_target_condition_timing(
        1, 2, hero, "target_turn_start", FixedDiceProvider([7]),
    )
    assert len(ticks) == 1
    assert ticks[0].damage_components[0].damage_type is DamageType.POISON
    assert ticks[0].damage_components[0].applied_total == 7
    assert hero.state.current_hp == hp_before - 7

    saves, _ = resolve_target_condition_timing(
        sequence, 2, hero, "target_turn_end", FixedDiceProvider([20]),
    )
    assert saves[0].save_succeeded is True
    assert saves[0].removed_condition_ids == ["poisoned"]
    assert "poisoned" not in hero.state.active_effect_ids


def test_periodic_damage_uses_typed_damage_defenses() -> None:
    setup = _setup()
    hero, vrock = setup.heroes[0], setup.monsters[0]
    hero.state.template.damage_resistances = [DamageType.POISON]
    hp_before = hero.state.current_hp
    apply_timed_condition(
        hero.state, "poisoned", vrock.combatant_id,
        source_effect_id="spores", applied_round=1,
        periodic_damage=_periodic_poison(),
    )

    events, _ = resolve_target_condition_timing(
        1, 2, hero, "target_turn_start", FixedDiceProvider([9]),
    )
    assert events[0].damage_components[0].applied_total == 4
    assert hero.state.current_hp == hp_before - 4

from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.conditions import attack_roll_condition_sources
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.timed_roll_effects import ability_check_disadvantage
from app.combat.zero_hp import apply_damage
from app.content.demo import build_demo_fighter
from app.content.monster_catalog_2014 import monster_by_id_2014, unsupported_mechanics_2014
from app.content.monster_catalog_2014 import load_catalog_2014
from app.domain.encounters import EncounterCombatant
from app.domain.weapons import DamageType


def _yeti_state():
    return build_combatant_state(monster_by_id_2014("yeti"))


def _member(state):
    return EncounterCombatant(combatant_id="yeti", side="monsters", position_ft=20, state=state)


def test_yeti_fear_of_fire_is_source_bound_and_certifiable() -> None:
    source = next(item for item in load_catalog_2014() if item.id == "yeti")
    assert "trait:Fear of Fire" not in unsupported_mechanics_2014(source)
    profile = monster_by_id_2014("yeti").damage_triggered_roll_penalties[0]
    assert profile.id == "fear-of-fire"
    assert profile.damage_types == [DamageType.FIRE]
    assert profile.attack_roll_disadvantage and profile.ability_check_disadvantage


def test_fire_damage_triggers_roll_penalties_but_cold_does_not() -> None:
    yeti = _yeti_state()
    target = build_combatant_state(build_demo_fighter())
    apply_damage(yeti, 1, damage_types={DamageType.FIRE})
    assert "fear-of-fire" in yeti.active_effect_ids
    assert ability_check_disadvantage(yeti) == 1
    _, disadvantage = attack_roll_condition_sources(yeti, target, 5, "target")
    assert disadvantage >= 1

    cold_yeti = _yeti_state()
    apply_damage(cold_yeti, 1, damage_types={DamageType.COLD})
    assert "fear-of-fire" not in cold_yeti.active_effect_ids
    assert ability_check_disadvantage(cold_yeti) == 0


def test_fear_of_fire_ends_at_end_of_next_turn_when_triggered_before_turn() -> None:
    state = _yeti_state(); apply_damage(state, 1, damage_types={DamageType.FIRE})
    member = _member(state)
    started, sequence = resolve_target_condition_timing(1, 1, member, "target_turn_start", FixedDiceProvider([1]))
    assert started == [] and sequence == 1
    ended, sequence = resolve_target_condition_timing(sequence, 1, member, "target_turn_end", FixedDiceProvider([1]))
    assert len(ended) == 1 and ended[0].removed_condition_ids == ["fear-of-fire"]
    assert "fear-of-fire" not in state.active_effect_ids and sequence == 2


def test_fear_of_fire_triggered_during_turn_survives_until_following_turn_end() -> None:
    state = _yeti_state(); member = _member(state)
    apply_damage(state, 1, damage_types={DamageType.FIRE})
    same_turn, sequence = resolve_target_condition_timing(1, 1, member, "target_turn_end", FixedDiceProvider([1]))
    assert same_turn == [] and "fear-of-fire" in state.active_effect_ids
    next_start, sequence = resolve_target_condition_timing(sequence, 2, member, "target_turn_start", FixedDiceProvider([1]))
    assert next_start == []
    next_end, _ = resolve_target_condition_timing(sequence, 2, member, "target_turn_end", FixedDiceProvider([1]))
    assert len(next_end) == 1 and "fear-of-fire" not in state.active_effect_ids

from app.combat.barbarian import FRENZY_2014_EFFECT_ID, end_rage, enter_rage
from app.combat.brutal_critical import brutal_critical_bonus_damage
from app.combat.dice import FixedDiceProvider
from app.combat.exhaustion import (
    attack_disadvantage_sources,
    d20_modifier,
    max_hp_after_exhaustion,
    saving_throw_disadvantage_sources,
    speed_after_exhaustion,
)
from app.combat.intimidating_presence_2014 import can_use_presence, resolve_intimidating_presence
from app.combat.state import build_combatant_state
from app.content.barbarian_berserker_2014_runtime import build_rokhan_stonefury_2014
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.domain.encounters import EncounterCombatant


def _member(template, combatant_id: str, side: str, position: int = 0) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_2014_berserker_levels_one_through_ten_are_isolated_from_2024() -> None:
    for level in range(1, 11):
        hero = build_rokhan_stonefury_2014(level)
        assert hero.ruleset == "2014"
        assert hero.level == level
        assert hero.weapon_masteries == []
        assert hero.weapon_attack.weapon.mastery_property is None
        assert all(attack.weapon.mastery_property is None for attack in hero.alternate_weapon_attacks)
        assert hero.source.startswith("D&D Basic Rules 2014")


def test_2014_exhaustion_uses_six_level_table_not_2024_numeric_penalty() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(10))
    state.exhaustion_level = 3
    assert d20_modifier(state) == 0
    assert attack_disadvantage_sources(state) == 1
    assert saving_throw_disadvantage_sources(state) == 1
    assert speed_after_exhaustion(state, 40) == 20

    state.exhaustion_level = 4
    assert max_hp_after_exhaustion(state, 100) == 50
    state.exhaustion_level = 5
    assert speed_after_exhaustion(state, 40) == 0


def test_2014_frenzy_marks_rage_and_adds_exactly_one_exhaustion_when_rage_ends() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(3))
    event = enter_rage(1, 1, state, "rokhan")
    assert event is not None
    assert "rage" in state.active_effect_ids
    assert FRENZY_2014_EFFECT_ID in state.active_effect_ids
    assert state.rage_max_round == 11
    assert state.exhaustion_level == 0

    level = end_rage(state)
    assert level == 1
    assert state.exhaustion_level == 1
    assert end_rage(state) is None
    assert state.exhaustion_level == 1


def test_2014_brutal_critical_adds_one_greataxe_die_only_on_critical() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(9))
    attack = state.template.weapon_attack
    assert brutal_critical_bonus_damage(state, attack, False) is None
    bonus = brutal_critical_bonus_damage(state, attack, True)
    assert bonus is not None
    source, count, sides, damage_type = bonus
    assert (source, count, sides) == ("Brutal Critical", 1, 12)
    assert damage_type == attack.weapon.damage_type


def test_2014_intimidating_presence_failed_save_frightens_and_success_grants_immunity() -> None:
    actor = _member(build_rokhan_stonefury_2014(10), "rokhan", "heroes", 0)
    target = _member(build_karnok_stoneward_2014(8), "target", "monsters", 5)
    assert can_use_presence(actor, target)

    failed = resolve_intimidating_presence(1, 1, actor, target, FixedDiceProvider([1]))
    assert failed is not None and failed.save_succeeded is False
    assert "frightened" in target.state.active_effect_ids

    actor2 = _member(build_rokhan_stonefury_2014(10), "rokhan-2", "heroes", 0)
    target2 = _member(build_karnok_stoneward_2014(8), "target-2", "monsters", 5)
    succeeded = resolve_intimidating_presence(1, 1, actor2, target2, FixedDiceProvider([20]))
    assert succeeded is not None and succeeded.save_succeeded is True
    actor2.state.action_available = True
    assert can_use_presence(actor2, target2) is False

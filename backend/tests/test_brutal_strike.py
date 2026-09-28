from app.combat.brutal_strike import (
    apply_brutal_strike_effect_policy,
    apply_hamstring_blow,
    apply_staggering_blow,
    apply_sundering_blow,
    brutal_strike_bonus_damage,
)
from app.combat.hit_modifiers import expire_source_turn_start_modifiers
from app.combat.modifier_stack import effective_speed, next_attack_against_flat_bonus
from app.combat.reckless_attack import RECKLESS_ATTACK_EFFECT_ID
from app.combat.state import build_combatant_state
from app.domain.progression import ProgressionCombatFeatures
from app.content.barbarian_progression import build_rokhan_stonefury_level


def _barbarian(level: int):
    template = build_rokhan_stonefury_level(level)
    state = build_combatant_state(template)
    state.active_effect_ids.append(RECKLESS_ATTACK_EFFECT_ID)
    return state, template.weapon_attack


def test_brutal_strike_is_one_1d10_strength_rider_per_turn_at_level_9():
    state, attack = _barbarian(9)
    first = brutal_strike_bonus_damage(state, attack, "1:rokhan", has_disadvantage=False)
    second = brutal_strike_bonus_damage(state, attack, "1:rokhan", has_disadvantage=False)
    assert first == ("Brutal Strike", 1, 10, attack.weapon.damage_type)
    assert second is None


def test_brutal_strike_is_blocked_by_disadvantage():
    state, attack = _barbarian(9)
    assert brutal_strike_bonus_damage(state, attack, "1:rokhan", has_disadvantage=True) is None


def test_brutal_strike_scales_to_2d10_at_level_17():
    state, attack = _barbarian(9)
    state.template.progression_features = ProgressionCombatFeatures(brutal_strike_damage_dice=2)
    assert brutal_strike_bonus_damage(state, attack, "1:rokhan", has_disadvantage=False) == (
        "Brutal Strike", 2, 10, attack.weapon.damage_type,
    )


def test_hamstring_blow_reuses_speed_modifier_and_expires_at_source_turn_start():
    state, _ = _barbarian(9)
    base_speed = effective_speed(state)
    assert apply_hamstring_blow(state, "rokhan", 1)
    assert effective_speed(state) == max(0, base_speed - 15)
    assert expire_source_turn_start_modifiers([state], "rokhan") == 1
    assert effective_speed(state) == base_speed


def test_staggering_blow_reuses_save_disadvantage_and_oa_suppression_modifiers():
    state, _ = _barbarian(9)
    assert apply_staggering_blow(state, "rokhan")
    kinds = {item.kind.value for item in state.active_modifiers if item.source_effect_id == "staggering-blow"}
    assert kinds == {"saving-throw-disadvantage", "opportunity-attack-suppressed"}
    save = next(item for item in state.active_modifiers if item.kind.value == "saving-throw-disadvantage")
    assert save.consume_on_saving_throw is True
    assert save.expires_at_start_of_source_turn is True


def test_sundering_blow_reuses_generic_next_attack_flat_bonus_and_does_not_help_source():
    state, _ = _barbarian(9)
    assert apply_sundering_blow(state, "rokhan")
    assert next_attack_against_flat_bonus(state, "rokhan") == 0
    assert next_attack_against_flat_bonus(state, "ally") == 5
    assert apply_sundering_blow(state, "other-barbarian")
    sundering = [item for item in state.active_modifiers if item.source_effect_id == "sundering-blow"]
    assert len(sundering) == 1
    assert sundering[0].source_id == "other-barbarian"


def test_brutal_strike_effect_policy_applies_legal_level_specific_choices():
    state, attack = _barbarian(9)
    target, _ = _barbarian(9)
    assert brutal_strike_bonus_damage(state, attack, "9:rokhan", has_disadvantage=False)
    assert apply_brutal_strike_effect_policy(state, target, "rokhan", "9:rokhan") == ("hamstring-blow",)

    state13, attack13 = _barbarian(13)
    target13, _ = _barbarian(9)
    assert brutal_strike_bonus_damage(state13, attack13, "13:rokhan", has_disadvantage=False)
    assert apply_brutal_strike_effect_policy(state13, target13, "rokhan", "13:rokhan") == ("staggering-blow",)

    state17, attack17 = _barbarian(17)
    target17, _ = _barbarian(9)
    assert brutal_strike_bonus_damage(state17, attack17, "17:rokhan", has_disadvantage=False)
    assert apply_brutal_strike_effect_policy(state17, target17, "rokhan", "17:rokhan") == (
        "staggering-blow", "hamstring-blow",
    )

from app.combat.brutal_strike import apply_hamstring_blow, brutal_strike_bonus_damage
from app.combat.hit_modifiers import expire_source_turn_start_modifiers
from app.combat.modifier_stack import effective_speed
from app.combat.reckless_attack import RECKLESS_ATTACK_EFFECT_ID
from app.combat.state import build_combatant_state
from app.content.hero_combat_feature_registry import compile_progression_feature_fields
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
    state.template.progression_features = compile_progression_feature_fields(("brutal-strike-2d10",), 17)
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

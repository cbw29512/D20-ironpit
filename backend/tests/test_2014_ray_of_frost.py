from app.combat.hit_modifiers import expire_source_turn_start_modifiers
from app.combat.modifier_stack import add_modifier, effective_speed
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.monster_spell_actions_2014 import SUPPORTED_DAMAGE_SPELLS_2014, _attack_spell


def test_ray_of_frost_binds_scaling_damage_and_source_start_slow() -> None:
    spell = _attack_spell("ray-of-frost", 0, 6, 5)

    assert "ray-of-frost" in SUPPORTED_DAMAGE_SPELLS_2014
    assert spell.range_ft == 60
    assert spell.damage_dice_count == 2
    assert spell.damage_dice_size == 8
    assert spell.damage_type == "cold"
    assert len(spell.on_hit_modifier_effects) == 1
    effect = spell.on_hit_modifier_effects[0]
    assert effect.kind == "speed"
    assert effect.flat_bonus == -10
    assert effect.expires_at_start_of_source_turn is True


def test_ray_of_frost_slow_expires_at_start_of_casters_next_turn() -> None:
    state = build_combatant_state(build_demo_fighter())
    base_speed = state.template.speed_ft
    spell = _attack_spell("ray-of-frost", 0, 6, 5)
    modifier = build_spell_modifier(
        "caster", "target", spell.id, spell.on_hit_modifier_effects[0], 0, round_number=1,
    )

    add_modifier(state, modifier)
    assert effective_speed(state) == max(0, base_speed - 10)
    assert modifier.expires_at_start_of_source_turn is True

    assert expire_source_turn_start_modifiers([state], "caster") == 1
    assert effective_speed(state) == base_speed

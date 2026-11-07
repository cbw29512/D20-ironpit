from app.combat.modifier_stack import effective_speed
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.capability_compiler import compile_combatant
from app.domain.weapons import DamageType


def _source_water_elemental():
    return next(monster for monster in load_monster_source_2014() if monster.id == "water-elemental")


def _template():
    source = _source_water_elemental()
    return compile_combatant(adapt_basic_monster_2014(source))


def test_water_elemental_freeze_binds_exact_source_parameters() -> None:
    source = _source_water_elemental()
    assert "Freeze" in source.trait_names
    assert "Freeze" not in unsupported_traits_2014(source)
    # Water Form remains unbound until its family lands; Freeze is cleared.
    assert "Water Form" in unsupported_traits_2014(source)

    template = _template()
    freeze_rules = [rule for rule in template.damage_taken_timed_effects if rule.source_name == "Freeze"]
    assert len(freeze_rules) == 1
    rule = freeze_rules[0]
    assert rule.trigger_damage_type is DamageType.COLD
    assert rule.target_turns == 1
    assert rule.speed_penalty_ft == 20
    assert rule.attack_roll_disadvantage is False


def test_cold_damage_applies_absolute_speed_penalty_until_next_turn_end() -> None:
    elemental = build_combatant_state(_template())
    base_speed = elemental.template.speed_ft
    assert base_speed == 40

    apply_damage(elemental, 1, damage_types={DamageType.FIRE})
    assert elemental.timed_effects == []
    assert effective_speed(elemental) == base_speed

    apply_damage(elemental, 1, damage_types={DamageType.COLD})
    assert len(elemental.timed_effects) == 1
    assert effective_speed(elemental) == max(0, base_speed - 20)

    # Penalty does not stack on further cold damage in the same window.
    apply_damage(elemental, 1, damage_types={DamageType.COLD})
    assert len(elemental.timed_effects) == 1
    assert effective_speed(elemental) == max(0, base_speed - 20)

import pytest

from app.combat.modifier_stack import effective_speed
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn
from app.content.monster_damage_taken_effects_2014 import damage_taken_timed_effects_2014
from app.domain.encounters import EncounterCombatant
from app.domain.damage_sources import DamageTakenTimedEffect
from scripts.browser_template_serializer import template_row
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.capability_compiler import compile_combatant
from app.domain.weapons import DamageType


def _source_water_elemental():
    return next(monster for monster in load_monster_source_2014() if monster.id == "water-elemental")


def _template():
    source = _source_water_elemental()
    return compile_combatant(adapt_monster_mechanics_2014(source))


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

def test_browser_template_exports_speed_penalty() -> None:
    # A handmade JS fixture cannot prove the real browser card contains this field.
    row = template_row(_template())
    freeze = next(x for x in row["damage_taken_timed_effects"]
                  if x["sourceName"] == "Freeze")
    assert freeze["triggerDamageType"] == "cold"
    assert freeze["speedPenaltyFt"] == 20
    assert freeze["targetTurns"] == 1


def test_source_drift_fails_closed() -> None:
    card = _source_water_elemental()
    assert "speed is reduced by 20 feet" in (card.source_traits or "")
    mutated = card.model_copy(update={
        "source_traits": card.source_traits.replace(
            "speed is reduced by 20 feet", "speed is reduced by 25 feet"
        ),
    })
    with pytest.raises(ValueError, match="Freeze"):
        damage_taken_timed_effects_2014(mutated)


def test_unrelated_card_can_declare_same_universal_speed_penalty() -> None:
    template = _template().model_copy(update={
        "damage_taken_timed_effects": [DamageTakenTimedEffect(
            source_id="generic-cold-debuff", source_name="Winter Sting",
            trigger_damage_type=DamageType.COLD, effect_id="generic-speed-loss",
            target_turns=1, speed_penalty_ft=7,
        )],
    })
    state = build_combatant_state(template)
    apply_damage(state, 1, damage_types={DamageType.COLD})
    assert effective_speed(state) == 33


def test_freeze_expires_at_end_of_next_turn_after_own_turn_trigger() -> None:
    state = build_combatant_state(_template())
    begin_turn(state)
    apply_damage(state, 1, damage_types={DamageType.COLD})
    assert state.timed_effects[0].expires_target_turn_count == 2
    member = EncounterCombatant(
        combatant_id="freeze-owner", side="monsters", position_ft=0, state=state,
    )
    events, _ = resolve_target_condition_timing(
        1, 1, member, "target_turn_end", FixedDiceProvider([1]),
    )
    assert events == []
    assert effective_speed(state) == 20
    begin_turn(state)
    events, _ = resolve_target_condition_timing(
        2, 2, member, "target_turn_end", FixedDiceProvider([1]),
    )
    assert events
    assert effective_speed(state) == 40

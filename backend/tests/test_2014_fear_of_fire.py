from app.combat.ability_checks import ability_check_roll_mode
from app.combat.attacks import resolve_attack
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.exhaustion import saving_throw_disadvantage_sources
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_ability_d20 import (
    timed_ability_d20_disadvantage_sources,
    timed_attack_roll_disadvantage_sources,
)
from app.combat.zero_hp import apply_damage
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant
from app.domain.models import RollMode
from app.domain.weapons import DamageType


def _source_yeti():
    return next(monster for monster in load_monster_source_2014() if monster.id == "yeti")


def _template():
    source = _source_yeti()
    assert basic_blockers_2014(source) == ()
    return compile_combatant(adapt_basic_monster_2014(source))


def test_yeti_fear_of_fire_binds_exact_source_parameters() -> None:
    source = _source_yeti()
    assert "Fear of Fire" in source.trait_names
    assert "Fear of Fire" not in unsupported_traits_2014(source)
    assert basic_blockers_2014(source) == ()

    template = _template()
    assert len(template.damage_taken_timed_effects) == 1
    rule = template.damage_taken_timed_effects[0]
    assert rule.source_name == "Fear of Fire"
    assert rule.trigger_damage_type is DamageType.FIRE
    assert rule.target_turns == 1
    assert rule.attack_roll_disadvantage is True
    assert rule.ability_check_disadvantage is True


def test_fire_damage_reuses_disadvantage_for_attacks_and_checks_not_saves() -> None:
    yeti = build_combatant_state(_template())
    target = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))

    apply_damage(yeti, 1, damage_types={DamageType.COLD})
    assert yeti.timed_effects == []

    apply_damage(yeti, 1, damage_types={DamageType.FIRE})
    assert len(yeti.timed_effects) == 1
    assert timed_attack_roll_disadvantage_sources(yeti) == 1
    assert ability_check_roll_mode(yeti) is RollMode.DISADVANTAGE
    assert timed_ability_d20_disadvantage_sources(yeti, "strength") == 0
    assert saving_throw_disadvantage_sources(yeti) == 0

    target.template.armor_class = 99
    event = resolve_attack(
        1, 1, yeti, target, yeti.template.weapon_attack, 5,
        FixedDiceProvider([18, 4]),
        actor_event_id="yeti", target_event_id="target", spend_action=False,
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.attack_roll.selected_roll == 4


def test_fear_of_fire_expires_at_end_of_next_actual_yeti_turn() -> None:
    template = _template()

    before_turn = build_combatant_state(template)
    apply_damage(before_turn, 1, damage_types={DamageType.FIRE})
    assert before_turn.timed_effects[0].expires_target_turn_count == 1
    member = EncounterCombatant(
        combatant_id="yeti-before", side="monsters", position_ft=0, state=before_turn,
    )
    begin_turn(before_turn)
    events, _ = resolve_target_condition_timing(
        1, 1, member, "target_turn_end", FixedDiceProvider([]),
    )
    assert events
    assert before_turn.timed_effects == []

    during_turn = build_combatant_state(template)
    begin_turn(during_turn)
    apply_damage(during_turn, 1, damage_types={DamageType.FIRE})
    assert during_turn.timed_effects[0].expires_target_turn_count == 2
    member = EncounterCombatant(
        combatant_id="yeti-during", side="monsters", position_ft=0, state=during_turn,
    )
    events, _ = resolve_target_condition_timing(
        1, 1, member, "target_turn_end", FixedDiceProvider([]),
    )
    assert events == []
    assert len(during_turn.timed_effects) == 1

    begin_turn(during_turn)
    events, _ = resolve_target_condition_timing(
        1, 2, member, "target_turn_end", FixedDiceProvider([]),
    )
    assert events
    assert during_turn.timed_effects == []

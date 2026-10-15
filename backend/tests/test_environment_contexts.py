from app.combat.ability_checks import ability_check_roll_mode
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.environment_contexts import (
    actor_inside_environment_context,
    environment_context_disadvantage_sources,
)
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_conditions import expire_start_of_turn_conditions
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.environment_context_reactions import sunlight_sensitivity_2014
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.paladin_devotion_2014_level20 import holy_nimbus_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.content.paladin_devotion_2024_level20 import holy_nimbus_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.environment_contexts import EmittedEnvironmentContext
from app.domain.models import RollMode
from app.domain.timed_self_buffs import TimedSelfBuffAction


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _sensitive_target(position: int = 25) -> EncounterCombatant:
    template = build_kael_stillwater_2014(1).model_copy(update={
        "environment_context_reactions": [sunlight_sensitivity_2014()],
    })
    return _member(template, "target", "monsters", position)


def _setup(target_position: int = 25):
    paladin = _member(build_aurelia_brightshield_2014(20), "aurelia", "heroes", 0)
    target = _sensitive_target(target_position)
    setup = EncounterSetup(
        heroes=[paladin], monsters=[target], hero_total_levels=20, monster_total_cr="1", ruleset="2014",
    )
    return setup, paladin, target


def _activate(paladin: EncounterCombatant) -> None:
    begin_turn(paladin.state)
    action = paladin.state.template.timed_self_buff_actions[0]
    event = resolve_timed_self_buff(1, 1, paladin, action)
    assert event.feature_id == "holy-nimbus"


def test_2014_holy_nimbus_declares_sunlight_context_not_a_name_check() -> None:
    nimbus = holy_nimbus_2014()
    assert nimbus.emitted_environment_contexts == [
        EmittedEnvironmentContext(context_id="sunlight", radius_ft=30),
    ]
    assert nimbus.id == "holy-nimbus"
    assert nimbus.start_turn_emanation_damage is not None
    assert nimbus.emitted_environment_contexts[0].radius_ft == nimbus.start_turn_emanation_damage.radius_ft


def test_2024_holy_nimbus_does_not_emit_sunlight() -> None:
    nimbus = holy_nimbus_2024(20, 4)
    assert nimbus.emitted_environment_contexts == []


def test_sunlight_reaction_imposes_attack_disadvantage_inside_live_nimbus() -> None:
    setup, paladin, target = _setup()
    _activate(paladin)

    assert actor_inside_environment_context(target, setup, "sunlight") is True
    assert environment_context_disadvantage_sources(target, setup, "attack_rolls") == 1
    assert environment_context_disadvantage_sources(
        target, setup, "sight_based_perception_checks",
    ) == 1
    assert ability_check_roll_mode(
        target.state, member=target, setup=setup, skill="perception", relies_on_sight=True,
    ) is RollMode.DISADVANTAGE
    assert ability_check_roll_mode(
        target.state, member=target, setup=setup, skill="perception", relies_on_sight=False,
    ) is RollMode.NORMAL

    target.position_ft = 5
    begin_turn(target.state)
    event = resolve_encounter_attack(
        2, 1, target, paladin, target.state.template.weapon_attack, 5,
        FixedDiceProvider([3, 17, 4]), setup,
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.attack_roll.selected_roll == 3


def test_sunlight_reaction_is_absent_out_of_range_or_without_context() -> None:
    setup, paladin, target = _setup(target_position=35)
    _activate(paladin)

    assert actor_inside_environment_context(target, setup, "sunlight") is False
    assert environment_context_disadvantage_sources(target, setup, "attack_rolls") == 0
    assert ability_check_roll_mode(
        target.state, member=target, setup=setup, skill="perception", relies_on_sight=True,
    ) is RollMode.NORMAL

    begin_turn(target.state)
    assert environment_context_disadvantage_sources(target, setup, "attack_rolls") == 0


def test_sunlight_reaction_ends_when_nimbus_expires() -> None:
    setup, paladin, target = _setup()
    _activate(paladin)
    expire_start_of_turn_conditions(2, 11, paladin, setup)

    assert actor_inside_environment_context(target, setup, "sunlight") is False
    assert environment_context_disadvantage_sources(target, setup, "attack_rolls") == 0
    assert ability_check_roll_mode(
        target.state, member=target, setup=setup, skill="perception", relies_on_sight=True,
    ) is RollMode.NORMAL


def test_no_penalty_without_reaction_data_or_active_emission() -> None:
    paladin = _member(build_aurelia_brightshield_2014(20), "aurelia", "heroes", 0)
    plain = _member(build_kael_stillwater_2014(1), "plain", "monsters", 25)
    setup = EncounterSetup(
        heroes=[paladin], monsters=[plain], hero_total_levels=20, monster_total_cr="1", ruleset="2014",
    )
    _activate(paladin)
    assert environment_context_disadvantage_sources(plain, setup, "attack_rolls") == 0

    unused = _sensitive_target()
    idle = _member(build_aurelia_brightshield_2014(20), "idle", "heroes", 0)
    idle_setup = EncounterSetup(
        heroes=[idle], monsters=[unused], hero_total_levels=20, monster_total_cr="1", ruleset="2014",
    )
    assert environment_context_disadvantage_sources(unused, idle_setup, "attack_rolls") == 0


def test_context_only_emission_applies_without_emanation_damage() -> None:
    paladin_template = build_aurelia_brightshield_2014(20)
    context_only = TimedSelfBuffAction(
        id="test-sunlight-zone",
        name="Test Sunlight Zone",
        action_cost="action",
        duration_rounds=10,
        emitted_environment_contexts=[
            EmittedEnvironmentContext(context_id="sunlight", radius_ft=30),
        ],
    )
    paladin_template = paladin_template.model_copy(update={"timed_self_buff_actions": [context_only]})
    paladin = _member(paladin_template, "source", "heroes", 0)
    target = _sensitive_target()
    setup = EncounterSetup(
        heroes=[paladin], monsters=[target], hero_total_levels=20, monster_total_cr="1", ruleset="2014",
    )
    begin_turn(paladin.state)
    resolve_timed_self_buff(1, 1, paladin, context_only)
    assert environment_context_disadvantage_sources(target, setup, "attack_rolls") == 1


def test_shadow_sunlight_weakness_is_permanent_source_binding_not_neutral() -> None:
    from app.content.environment_context_reactions import (
        sunlight_weakness_2014, verified_sunlight_weakness_2014,
    )
    from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
    from app.content.monster_source_2014 import load_monster_source_2014
    from app.content.monster_trait_bindings_2014 import (
        bound_trait_names_2014, environment_context_reactions_2014,
    )

    source = next(m for m in load_monster_source_2014() if m.id == "shadow")
    assert verified_sunlight_weakness_2014(source)
    assert "Sunlight Weakness" in bound_trait_names_2014(source)
    assert "Sunlight Weakness" not in unsupported_traits_2014(source)
    assert environment_context_reactions_2014(source) == [sunlight_weakness_2014()]
    altered = source.model_copy(update={
        "source_traits": (source.source_traits or "").replace(
            "saving throws", "unrelated words",
        ),
    })
    assert not verified_sunlight_weakness_2014(altered)
    assert "Sunlight Weakness" in unsupported_traits_2014(altered)


def test_full_sunlight_weakness_affects_every_d20_roll_kind_and_clears_on_exit() -> None:
    from app.content.environment_context_reactions import sunlight_weakness_2014
    from app.combat.saving_throw_rolls import saving_throw_mode

    setup, paladin, target = _setup()
    original_template = target.state.template
    target.state.template = original_template.model_copy(update={
        "environment_context_reactions": [sunlight_weakness_2014()],
    })
    # The weakness belongs to the template permanently even with no exposure.
    assert environment_context_disadvantage_sources(target, setup, "saving_throws") == 0
    _activate(paladin)
    for kind in ("attack_rolls", "ability_checks", "saving_throws"):
        assert environment_context_disadvantage_sources(target, setup, kind) == 1
    assert ability_check_roll_mode(target.state, member=target, setup=setup) is RollMode.DISADVANTAGE
    assert ability_check_roll_mode(
        target.state, member=target, setup=setup, skill="perception", relies_on_sight=False,
    ) is RollMode.DISADVANTAGE
    assert saving_throw_mode(
        target.state, "wisdom", member=target, setup=setup,
    ) is RollMode.DISADVANTAGE
    target.position_ft = 35
    assert environment_context_disadvantage_sources(target, setup, "saving_throws") == 0
    assert saving_throw_mode(
        target.state, "wisdom", member=target, setup=setup,
    ) is RollMode.NORMAL
    assert target.state.template.environment_context_reactions == [sunlight_weakness_2014()]

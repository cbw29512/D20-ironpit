from __future__ import annotations

from app.combat.ability_checks import ability_check_roll_mode
from app.combat.environment_contexts import (
    actor_inside_environment_context,
    environment_context_disadvantage_sources,
)
from app.combat.environment_context_actions import resolve_environment_context_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_bright_light_contexts_2014 import (
    light_sensitivity_reaction_2014,
    mutable_bright_light_actions_2014,
    permanent_bright_light_contexts_2014,
)
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import bound_trait_names_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode


def _sources():
    return {item.id: item for item in load_monster_source_2014()}


def _member(template, ident: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=ident,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_complete_327_card_scan_binds_fixed_and_mutable_emitters_and_exact_reaction() -> None:
    sources = _sources()
    emitters = {
        monster.id: [item.radius_ft for item in permanent_bright_light_contexts_2014(monster)]
        for monster in sources.values()
        if permanent_bright_light_contexts_2014(monster)
    }
    reactors = {
        monster.id for monster in sources.values()
        if light_sensitivity_reaction_2014(monster) is not None
    }
    assert emitters == {
        "azer": [10], "fire-elemental": [30],
        "giant-fire-beetle": [10], "nightmare": [10],
    }
    assert reactors == {"cloaker"}
    mutable = {
        monster.id: [action.name for action in mutable_bright_light_actions_2014(monster)]
        for monster in sources.values() if mutable_bright_light_actions_2014(monster)
    }
    assert mutable == {
        "flameskull": ["Illumination"],
        "magmin": ["Ignited Illumination"],
        "will-o-wisp": ["Variable Illumination"],
    }

    for monster_id in emitters:
        source = sources[monster_id]
        assert "Illumination" in bound_trait_names_2014(source)
        assert "Illumination" not in unsupported_traits_2014(source)
    assert "Light Sensitivity" in bound_trait_names_2014(sources["cloaker"])
    assert "Light Sensitivity" not in unsupported_traits_2014(sources["cloaker"])

    for monster_id, names in mutable.items():
        for name in names:
            assert name in bound_trait_names_2014(sources[monster_id])
            assert name not in unsupported_traits_2014(sources[monster_id])


def test_mutable_light_modes_are_fight_local_and_spend_printed_economy() -> None:
    sources = _sources()
    magmin_template = compile_combatant(adapt_basic_monster_2014(sources["magmin"]))
    action = magmin_template.environment_context_control_actions[0]
    magmin = _member(magmin_template, "magmin", "heroes", 0)
    second_fight = _member(magmin_template, "magmin-2", "heroes", 0)
    assert magmin.state.environment_context_modes[action.id] == "extinguished"
    assert second_fight.state.environment_context_modes[action.id] == "extinguished"

    ablaze = next(mode for mode in action.modes if mode.id == "ablaze")
    event = resolve_environment_context_action(1, 1, magmin, action, ablaze)
    assert magmin.state.environment_context_modes[action.id] == "ablaze"
    assert magmin.state.bonus_action_available is False
    assert second_fight.state.environment_context_modes[action.id] == "extinguished"
    assert event.feature_id == "Ignited Illumination"

    wisp = compile_combatant(adapt_basic_monster_2014(sources["will-o-wisp"]))
    variable = wisp.environment_context_control_actions[0]
    assert [mode.emitted_contexts[0].radius_ft for mode in variable.modes] == list(range(5, 21))
    assert variable.initial_mode_id == "bright-20"


def test_light_sensitivity_uses_permanent_bright_light_and_sunlight_implication() -> None:
    sources = _sources()
    azer_template = compile_combatant(adapt_basic_monster_2014(sources["azer"]))
    # The Cloaker card still has independent attack/action blockers. Exercise
    # its exact compiled reaction on an unrelated admitted template so this
    # shared primitive is proved without bypassing those blockers.
    cloaker_template = azer_template.model_copy(update={
        "id": "synthetic-light-sensitive-card",
        "name": "Synthetic Light-sensitive Card",
        "emitted_environment_contexts": [],
        "environment_context_reactions": [
            light_sensitivity_reaction_2014(sources["cloaker"]),
        ],
    })
    cloaker = _member(cloaker_template, "cloaker", "monsters", 10)
    azer = _member(azer_template, "azer", "heroes", 0)
    setup = EncounterSetup(
        heroes=[azer], monsters=[cloaker], hero_total_levels=1,
        monster_total_cr="8", ruleset="2014",
    )

    assert actor_inside_environment_context(cloaker, setup, "bright_light")
    assert not actor_inside_environment_context(cloaker, setup, "sunlight")
    assert environment_context_disadvantage_sources(cloaker, setup, "attack_rolls") == 1
    assert environment_context_disadvantage_sources(
        cloaker, setup, "sight_based_perception_checks",
    ) == 1
    assert ability_check_roll_mode(
        cloaker.state, member=cloaker, setup=setup,
        skill="perception", relies_on_sight=True,
    ) is RollMode.DISADVANTAGE
    assert ability_check_roll_mode(
        cloaker.state, member=cloaker, setup=setup,
        skill="perception", relies_on_sight=False,
    ) is RollMode.NORMAL

    cloaker.position_ft = 15
    assert not actor_inside_environment_context(cloaker, setup, "bright_light")
    assert environment_context_disadvantage_sources(cloaker, setup, "attack_rolls") == 0

    sunlight_source_template = azer_template.model_copy(update={
        "emitted_environment_contexts": [
            azer_template.emitted_environment_contexts[0].model_copy(update={
                "context_id": "sunlight",
            }),
        ],
    })
    sunlight_source = _member(sunlight_source_template, "sunlight", "heroes", 0)
    cloaker.position_ft = 10
    sunlight_setup = setup.model_copy(update={"heroes": [sunlight_source]})
    assert actor_inside_environment_context(cloaker, sunlight_setup, "sunlight")
    assert actor_inside_environment_context(cloaker, sunlight_setup, "bright_light")
    assert environment_context_disadvantage_sources(cloaker, sunlight_setup, "attack_rolls") == 1


def test_complete_source_clause_is_required_and_cards_remain_immutable() -> None:
    sources = _sources()
    cloaker = sources["cloaker"]
    azer = sources["azer"]
    cloaker_text = cloaker.source_traits
    azer_text = azer.source_traits
    altered_cloaker = cloaker.model_copy(update={
        "source_traits": (cloaker.source_traits or "").replace("bright light", "dim light"),
    })
    altered_azer = azer.model_copy(update={
        "source_traits": (azer.source_traits or "").replace("10 feet", "20 feet"),
    })
    assert light_sensitivity_reaction_2014(altered_cloaker) is None
    assert permanent_bright_light_contexts_2014(altered_azer) == []
    assert cloaker.source_traits == cloaker_text
    assert azer.source_traits == azer_text

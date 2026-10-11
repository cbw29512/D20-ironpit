"""2014 Steadfast binds to the same contextual immunity primitive as every source."""
from types import SimpleNamespace
from unittest.mock import patch

from app.combat.condition_immunity import condition_is_immune
from app.content.monster_passive_grants_2014 import conditional_immunity_grants_2014
from app.domain.modifiers import CombatModifier, ModifierKind


def _actor(*, bound=True):
    template = SimpleNamespace(
        name="Steadfast test combatant", ruleset="2014",
        source_trait_names=["Steadfast"], condition_immunities=[],
        progression_features=SimpleNamespace(mindless_rage=False),
    )
    state = SimpleNamespace(
        template=template, active_modifiers=[], active_effect_ids=[], timed_effects=[],
    )
    if bound:
        state.active_modifiers.append(CombatModifier(
            id="source:steadfast:passive", source_id="bearded-devil",
            source_effect_id="steadfast", source_name="Steadfast",
            kind=ModifierKind.CONDITION_IMMUNITY, condition_id="frightened",
            required_visible_active_ally_within_ft=30,
        ))
    return SimpleNamespace(state=state)


def test_source_binding_uses_data_not_name_dispatch():
    monster = SimpleNamespace(name="Bearded Devil", trait_names={"Steadfast"})
    grants = conditional_immunity_grants_2014(monster)
    assert len(grants) == 1
    assert grants[0].source_name == "Steadfast"
    assert grants[0].condition_id == "frightened"
    assert grants[0].required_visible_active_ally_within_ft == 30
    assert conditional_immunity_grants_2014(
        SimpleNamespace(name="Other", trait_names=set()),
    ) == []


def test_condition_immunity_ignores_printed_name_without_bound_modifier():
    actor, setup = _actor(bound=False), object()
    with patch("app.combat.ally_context.has_visible_active_ally_within") as eligible:
        assert not condition_is_immune(actor.state, "frightened", actor=actor, setup=setup)
        eligible.assert_not_called()


def test_generic_condition_immunity_follows_live_ally_range_visibility():
    actor, setup = _actor(), object()
    with patch("app.combat.ally_context.has_visible_active_ally_within", return_value=True) as eligible:
        assert condition_is_immune(actor.state, "frightened", actor=actor, setup=setup)
        eligible.assert_called_once_with(actor, setup, 30)
        assert not condition_is_immune(actor.state, "charmed", actor=actor, setup=setup)
    with patch("app.combat.ally_context.has_visible_active_ally_within", return_value=False):
        assert not condition_is_immune(actor.state, "frightened", actor=actor, setup=setup)
    assert not condition_is_immune(actor.state, "frightened")


def test_condition_immunity_is_fight_state_not_template_mutation():
    actor = _actor()
    assert actor.state.template.condition_immunities == []
    assert actor.state.active_modifiers[0].source_effect_id == "steadfast"

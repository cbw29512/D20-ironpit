"""Steadfast never grants unconditional or out-of-range immunity."""
from types import SimpleNamespace
from unittest.mock import patch

from app.combat.steadfast_condition_immunity import steadfast_frightened_immunity


def _actor(*, traits=("Steadfast",), ruleset="2014"):
    return SimpleNamespace(state=SimpleNamespace(template=SimpleNamespace(
        ruleset=ruleset, source_trait_names=list(traits)
    )))


def test_steadfast_requires_printed_source_and_correct_condition():
    with patch("app.combat.steadfast_condition_immunity.has_visible_active_ally_within") as eligible:
        assert not steadfast_frightened_immunity(_actor(), None, "charmed")
        assert not steadfast_frightened_immunity(_actor(traits=()), None, "frightened")
        assert not steadfast_frightened_immunity(_actor(ruleset="2024"), None, "frightened")
        eligible.assert_not_called()


def test_steadfast_follows_live_ally_range_and_visibility():
    actor, setup = _actor(), object()
    with patch("app.combat.steadfast_condition_immunity.has_visible_active_ally_within") as eligible:
        eligible.return_value = True
        assert steadfast_frightened_immunity(actor, setup, "frightened")
        eligible.assert_called_once_with(actor, setup, 30)
        eligible.return_value = False
        assert not steadfast_frightened_immunity(actor, setup, "frightened")


def test_universal_condition_resolver_accepts_encounter_scoped_steadfast():
    from app.combat.condition_immunity import condition_is_immune
    actor = _actor()
    actor.state.template.condition_immunities = []
    actor.state.template.progression_features = SimpleNamespace(mindless_rage=False)
    from app.domain.modifiers import CombatModifier, ModifierKind
    actor.state.active_modifiers = [CombatModifier(
        id="steadfast:passive", source_id="bearded-devil", source_effect_id="steadfast",
        source_name="Steadfast", kind=ModifierKind.CONDITION_IMMUNITY,
        condition_id="frightened", required_visible_active_ally_within_ft=30,
    )]
    actor.state.active_effect_ids = []
    # The universal debuff pipeline always reads timed effects and uses
    # the immutable template identity for diagnostic logging.
    actor.state.timed_effects = []
    actor.state.template.name = "Steadfast test combatant"
    setup = object()
    with patch("app.combat.ally_context.has_visible_active_ally_within", return_value=True) as eligible:
        assert condition_is_immune(actor.state, "frightened", actor=actor, setup=setup)
        eligible.assert_called_once_with(actor, setup, 30)
        assert not condition_is_immune(actor.state, "charmed", actor=actor, setup=setup)
    with patch("app.combat.ally_context.has_visible_active_ally_within", return_value=False):
        assert not condition_is_immune(actor.state, "frightened", actor=actor, setup=setup)
    assert not condition_is_immune(actor.state, "frightened")  # No encounter context, no conditional protection.


def test_source_binding_is_data_not_a_steadfast_engine_branch():
    from app.content.monster_passive_grants_2014 import conditional_immunity_grants_2014
    monster = SimpleNamespace(name="Bearded Devil", trait_names={"Steadfast"})
    grants = conditional_immunity_grants_2014(monster)
    assert len(grants) == 1
    assert grants[0].condition_id == "frightened"
    assert grants[0].required_visible_active_ally_within_ft == 30
    assert conditional_immunity_grants_2014(SimpleNamespace(name="Other", trait_names=set())) == []

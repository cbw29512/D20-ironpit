from __future__ import annotations

from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.timed_emanations import resolve_target_turn_start_emanations
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import passive_trait_timed_self_buffs_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _source(name: str):
    return next(item for item in load_monster_source_2014() if item.name == name)


def _member(name: str, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    template = compile_combatant(adapt_basic_monster_2014(_source(name)))
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def test_stench_source_parameters_are_parsed_from_pinned_srd_text() -> None:
    ghast = passive_trait_timed_self_buffs_2014(_source("Ghast"))[0]
    hezrou = passive_trait_timed_self_buffs_2014(_source("Hezrou"))[0]

    assert ghast.activation_timing == "passive"
    assert ghast.duration_rounds == 1
    assert ghast.expiry_timing == "target_turn_start"
    assert ghast.hostile_start_turn_condition_aura.radius_ft == 5
    assert ghast.hostile_start_turn_condition_aura.save_dc == 10

    assert hezrou.activation_timing == "passive"
    assert hezrou.hostile_start_turn_condition_aura.radius_ft == 10
    assert hezrou.hostile_start_turn_condition_aura.save_dc == 14

    for action in (ghast, hezrou):
        aura = action.hostile_start_turn_condition_aura
        assert aura.save_ability == "constitution"
        assert aura.condition_id == "poisoned"
        assert aura.success_immunity is True
        assert aura.source_is_magical is False


def test_stench_binding_unlocks_hezrou_and_leaves_only_ghast_other_trait() -> None:
    hezrou = _source("Hezrou")
    ghast = _source("Ghast")

    assert unsupported_traits_2014(hezrou) == ()
    assert basic_blockers_2014(hezrou) == ()
    assert "Stench" not in unsupported_traits_2014(ghast)
    assert unsupported_traits_2014(ghast) == ("Turning Defiance",)


def test_stench_failure_uses_universal_poisoned_until_next_target_turn_start() -> None:
    source = _member("Hezrou", "hezrou", "monsters", 0)
    target = _member("Commoner", "commoner", "heroes", 5)
    setup = EncounterSetup(
        heroes=[target], monsters=[source], hero_total_levels=1,
        monster_total_cr=_source("Hezrou").challenge_rating, ruleset="2014",
    )

    events, sequence = resolve_target_turn_start_emanations(
        1, 1, target, setup, FixedDiceProvider([1]), turn_key="1:commoner",
    )
    assert sequence == 2
    assert len(events) == 1
    assert events[0].feature_id == "hezrou-stench"
    assert events[0].save_succeeded is False
    assert "poisoned" in target.state.active_effect_ids

    poison = next(
        effect for effect in target.state.timed_effects
        if effect.effect_id == "poisoned" and effect.source_id == "hezrou"
    )
    assert poison.source_effect_id == "hezrou-stench"
    assert poison.expiry_timing == "target_turn_start"
    assert poison.expires_round == 2
    assert poison.repeat_save_ability is None

    expiry, final_sequence = resolve_target_condition_timing(
        sequence, 2, target, "target_turn_start", FixedDiceProvider([]), setup,
    )
    assert final_sequence == sequence + 1
    assert expiry[0].removed_condition_ids == ["poisoned"]
    assert "poisoned" not in target.state.active_effect_ids


def test_stench_success_grants_source_specific_match_immunity_only_in_fight_state() -> None:
    source = _member("Hezrou", "hezrou", "monsters", 0)
    target = _member("Commoner", "commoner", "heroes", 5)
    setup = EncounterSetup(
        heroes=[target], monsters=[source], hero_total_levels=1,
        monster_total_cr=_source("Hezrou").challenge_rating, ruleset="2014",
    )

    events, sequence = resolve_target_turn_start_emanations(
        1, 1, target, setup, FixedDiceProvider([20]), turn_key="1:commoner",
    )
    assert len(events) == 1
    assert events[0].save_succeeded is True
    immunity_id = "hezrou-stench:success-immunity:hezrou"
    assert any(effect.effect_id == immunity_id for effect in target.state.timed_effects)
    assert immunity_id not in target.state.template.source_trait_names

    repeated, repeated_sequence = resolve_target_turn_start_emanations(
        sequence, 2, target, setup, FixedDiceProvider([1]), turn_key="2:commoner",
    )
    assert repeated == []
    assert repeated_sequence == sequence

    fresh = _member("Commoner", "fresh-commoner", "heroes", 5)
    assert not any(effect.effect_id == immunity_id for effect in fresh.state.timed_effects)
    assert "poisoned" not in fresh.state.active_effect_ids


def test_dead_passive_aura_source_does_not_emit_stench() -> None:
    source = _member("Hezrou", "hezrou", "monsters", 0)
    target = _member("Commoner", "commoner", "heroes", 5)
    source.state.is_alive = False
    source.state.is_dead = True
    source.state.current_hp = 0
    setup = EncounterSetup(
        heroes=[target], monsters=[source], hero_total_levels=1,
        monster_total_cr=_source("Hezrou").challenge_rating, ruleset="2014",
    )

    events, sequence = resolve_target_turn_start_emanations(
        1, 1, target, setup, FixedDiceProvider([1]), turn_key="1:commoner",
    )
    assert events == []
    assert sequence == 1

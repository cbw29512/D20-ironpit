from __future__ import annotations

from app.combat.debuff_counters import (
    debuff_is_countered,
    difficult_terrain_multiplier,
    movement_counter_cost,
)
from app.combat.opening_modifiers import opening_modifiers
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_freedom_of_movement_2014 import (
    passive_freedom_of_movement_grants_2014,
)
from app.content.monster_trait_bindings_2014 import progression_features_2014
from scripts.browser_template_serializer import template_row


def _source(card_id: str):
    return next(item for item in load_monster_source_2014() if item.id == card_id)


def _compiled_probe(source):
    """Compile the independent trait even while the source card has unrelated blockers."""
    base = adapt_monster_mechanics_2014(_source("commoner"))
    return compile_combatant(base.model_copy(update={
        "id": "2014-source-neutral-passive-probe",
        "name": "Source-neutral Passive Probe",
        "progression_features": progression_features_2014(source),
    }))


def test_full_2014_scan_finds_only_complete_passive_movement_clause() -> None:
    applicable = [
        monster.id
        for monster in load_monster_source_2014()
        if passive_freedom_of_movement_grants_2014(monster)
    ]
    assert len(load_monster_source_2014()) == 327
    assert applicable == ["kraken"]


def test_source_proof_is_identity_independent_and_fails_closed() -> None:
    source = _source("kraken")
    renamed = source.model_copy(update={"id": "renamed-card", "name": "Renamed Card"})
    assert len(passive_freedom_of_movement_grants_2014(renamed)) == 5

    changed = source.model_copy(update={
        "source_traits": source.source_traits.replace("5 feet", "10 feet"),
    })
    assert passive_freedom_of_movement_grants_2014(changed) == []


def test_kraken_compiles_exact_passive_counters_for_python_and_browser() -> None:
    template = _compiled_probe(_source("kraken"))
    grants = template.progression_features.passive_debuff_counter_grants
    signatures = {
        (
            grant.counter.debuff_id,
            grant.counter.source_scope,
            grant.counter.mode,
            grant.counter.movement_cost_ft,
        )
        for grant in grants
    }
    assert signatures == {
        ("difficult-terrain", "any", "prevent", 0),
        ("speed-reduction", "magical", "prevent", 0),
        ("restrained", "magical", "prevent", 0),
        ("grappled", "nonmagical", "remove-with-movement", 5),
        ("restrained", "nonmagical", "remove-with-movement", 5),
    }
    assert all(grant.source_name == "Freedom of Movement" for grant in grants)

    browser = template_row(template)["passive_debuff_counter_grants"]
    assert browser == [grant.model_dump(mode="json") for grant in grants]


def test_kraken_passive_uses_shared_counter_runtime_without_spell_state() -> None:
    template = _compiled_probe(_source("kraken"))
    state = build_combatant_state(template)
    state.active_modifiers = opening_modifiers(template)

    assert difficult_terrain_multiplier(state) == 1
    assert debuff_is_countered(state, "speed-reduction", source_is_magical=True)
    assert debuff_is_countered(state, "restrained", source_is_magical=True)
    assert not debuff_is_countered(state, "paralyzed", source_is_magical=True)
    assert not debuff_is_countered(state, "grappled", source_is_magical=False)
    assert movement_counter_cost(state, "grappled", source_is_magical=False) == 5
    assert movement_counter_cost(state, "restrained", source_is_magical=False) == 5
    assert movement_counter_cost(state, "grappled", source_is_magical=True) is None

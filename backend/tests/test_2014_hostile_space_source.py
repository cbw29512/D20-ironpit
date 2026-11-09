"""Source-to-engine and universal grid parity for hostile-space stopping."""
from __future__ import annotations

import pytest

from app.combat.grid_pathing import plan_movement_toward
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_goblin_warrior
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_hostile_overlap_source_2014 import (
    source_proven_hostile_overlap_traits_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant
from app.domain.grid import BattleMapDefinition, GridPosition
from scripts.browser_template_serializer import template_row

MAP = BattleMapDefinition(id="hostile-overlap", width_squares=8, height_squares=8)


def _card(source_id: str):
    return next(card for card in load_monster_source_2014() if card.id == source_id)


def _member(identifier: str, side: str, x: int, y: int) -> EncounterCombatant:
    state = build_combatant_state(build_goblin_warrior().model_copy(
        update={"id": identifier, "name": identifier},
    ))
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(
        combatant_id=identifier, side=side, position_ft=0, state=state,
    )


@pytest.mark.parametrize("source_id,trait", [
    ("air-elemental", "Air Form"),
    ("water-elemental", "Water Form"),
])
def test_exact_source_compiles_to_real_browser_flag(source_id: str, trait: str):
    card = _card(source_id)
    unchanged = card.model_dump_json()
    assert trait in source_proven_hostile_overlap_traits_2014(card)
    assert trait not in unsupported_traits_2014(card)
    template = compile_combatant(adapt_monster_mechanics_2014(card))
    assert template.source_allows_hostile_overlap is True
    assert template_row(template)["source_allows_hostile_overlap"] is True
    assert card.model_dump_json() == unchanged


@pytest.mark.parametrize("source_id,trait", [
    ("air-elemental", "Air Form"),
    ("water-elemental", "Water Form"),
])
def test_extra_or_missing_movement_clause_fails_closed(source_id: str, trait: str):
    card = _card(source_id)
    printed = card.source_traits or ""
    assert "and stop there" in printed
    tampered = card.model_copy(update={
        "source_traits": printed.replace("and stop there", "and keep moving"),
    })
    assert trait not in source_proven_hostile_overlap_traits_2014(tampered)
    assert trait in unsupported_traits_2014(tampered)
    assert not compile_combatant(
        adapt_monster_mechanics_2014(tampered)
    ).source_allows_hostile_overlap


def test_renamed_source_label_reuses_the_same_combat_flag():
    card = _card("water-elemental")
    renamed = card.model_copy(update={
        "trait_names": ["Flow Through" if n == "Water Form" else n
                        for n in card.trait_names],
        "source_traits": (card.source_traits or "").replace(
            "<strong>Water Form.</strong>", "<strong>Flow Through.</strong>",
        ),
    })
    assert source_proven_hostile_overlap_traits_2014(renamed) == frozenset({
        "Flow Through",
    })
    assert compile_combatant(
        adapt_monster_mechanics_2014(renamed)
    ).source_allows_hostile_overlap


def test_shared_grid_movement_can_stop_on_hostile_but_never_ally():
    mover = _member("generic-flowing-form", "monsters", 0, 0)
    target = _member("target", "heroes", 2, 2)
    everyone = [mover, target]
    denied = plan_movement_toward(MAP, mover, target, everyone, 0, 30)
    assert not denied.path or denied.path[-1] != target.state.position
    allowed = plan_movement_toward(
        MAP, mover, target, everyone, 0, 30,
        source_allows_hostile_overlap=True,
    )
    assert allowed.goal_reachable
    assert allowed.path[-1] == target.state.position
    assert allowed.movement_cost_ft > 0

    ally = _member("friendly", "monsters", 2, 2)
    with_ally = plan_movement_toward(
        MAP, mover, target, [*everyone, ally], 0, 30,
        source_allows_hostile_overlap=True,
    )
    assert not with_ally.path or with_ally.path[-1] != target.state.position

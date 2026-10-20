"""Source-verified Banshee Wail binds to the shared RAW all-creature save engine."""
from __future__ import annotations

import re

import pytest

from app.combat.area_save_actions import choose_area_save, resolve_area_save
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_save_outcome_bindings_2014 import source_proven_asymmetric_saves_2014
from app.content.monster_save_capabilities_2014 import save_capabilities_2014, save_resources_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.combatants import DamageType
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition


def _source():
    return next(row for row in load_monster_source_2014() if row.id == "banshee")


def _wail_only_source():
    # Isolated Wail-only test variant; full source now also binds Horrifying Visage.
    source = _source()
    without_visage = re.sub(
        r"<p><em><strong>Horrifying Visage\.</strong></em>.*?</p>",
        "", source.source_actions or "", flags=re.S,
    )
    assert "Horrifying Visage" not in without_visage
    return source.model_copy(update={
        "action_names": [name for name in source.action_names if name != "Horrifying Visage"],
        "source_actions": without_visage,
    })


def _member(cid, side, x, template):
    actor = EncounterCombatant(
        combatant_id=cid, side=side, position_ft=x * 5,
        state=build_combatant_state(template),
    )
    actor.state.position = GridPosition(x=x, y=1)
    return actor


def _arena():
    template = compile_combatant(adapt_basic_monster_2014(_wail_only_source()))
    actor = _member("banshee", "monsters", 1, template)
    living = _member("living-ally", "monsters", 2,
                     build_aurelia_brightshield_2014(1).model_copy(update={"max_hp": 60, "kind": "monster"}))
    living.state.temporary_hp = 7
    construct = _member("construct-ally", "monsters", 3,
                        build_aurelia_brightshield_2014(1).model_copy(update={"creature_type": "construct"}))
    undead = _member("undead-ally", "monsters", 4,
                     build_aurelia_brightshield_2014(1).model_copy(update={"creature_type": "undead"}))
    hero = _member("enemy-hero", "heroes", 5,
                   build_aurelia_brightshield_2014(1).model_copy(update={"max_hp": 60}))
    deafened = _member("deafened-enemy", "heroes", 6, build_aurelia_brightshield_2014(1))
    deafened.state.active_effect_ids.append("deafened")
    setup = EncounterSetup(
        heroes=[hero, deafened], monsters=[actor, living, construct, undead],
        hero_total_levels=2, monster_total_cr="4", ruleset="2014",
        map_definition=BattleMapDefinition(id="banshee-wail", width_squares=12, height_squares=12),
    )
    return actor, living, hero, construct, undead, deafened, setup


def test_printed_wail_compiles_exact_save_parameters_alongside_visual_fear():
    source = _source()
    matches = source_proven_asymmetric_saves_2014(source)
    assert len(matches) == 1
    action = matches[0]
    assert action.name == "Wail (1/Day)"
    assert action.target_scope == "all-other-creatures"
    assert action.area.radius_ft == 30 and action.dc == 13
    assert action.requires_target_hearing
    assert action.excluded_target_creature_types == ["construct", "undead"]
    assert action.prohibited_environment_context_id == "sunlight"
    assert action.failure_sets_zero_hp and action.damage_only_on_success
    assert action.damage.count == 3 and action.damage.size == 6
    assert action.damage_type == DamageType.PSYCHIC
    assert len(save_capabilities_2014(source)) == 2
    assert [(r.id, r.max_uses) for r in save_resources_2014(source)] == [("wail", 1)]
    assert "source:extra-action" not in basic_blockers_2014(source)
    assert "source:extra-action" not in basic_blockers_2014(_wail_only_source())


def test_modified_effect_clause_fails_closed_instead_of_silently_admitting():
    source = _source()
    for old, new in (
        ("All other creatures", "All enemy creatures"),
        ("aren’t", "are"),  # If this word is absent, no unrelated body changes are permitted.
        ("drops to 0 hit points", "takes 0 damage"),
        ("that can hear her", "that can see her"),
    ):
        if old not in (source.source_actions or ""):
            continue
        mutant = source.model_copy(update={"source_actions": source.source_actions.replace(old, new)})
        assert source_proven_asymmetric_saves_2014(mutant) == []
        assert "source:extra-action" in basic_blockers_2014(mutant)


def test_wail_friendly_monster_dies_but_eligible_enemy_takes_success_damage():
    actor, living, hero, construct, undead, deafened, setup = _arena()
    selected = choose_area_save(actor, setup)
    assert selected is not None
    action, placement = selected
    assert set(placement.target_ids) == {"living-ally", "enemy-hero"}
    assert actor.combatant_id not in placement.target_ids
    # Three shared Psychic dice first, then one independent save per target:
    # enemy hero succeeds with 20; living friendly monster fails with 1.
    events, _ = resolve_area_save(
        1, 1, actor, setup, action, placement, FixedDiceProvider([1, 1, 1, 20, 1]),
    )
    assert len(events) == 2
    by_target = {event.target_id: event for event in events}
    assert by_target["enemy-hero"].save_succeeded is True
    assert hero.state.current_hp == 57
    assert by_target["living-ally"].save_succeeded is False
    assert living.state.current_hp == 0 and living.state.is_dead
    assert living.state.temporary_hp == 7
    assert by_target["living-ally"].damage_roll is None
    assert all("Wail (1/Day)" in event.description for event in events)
    assert not set(by_target) & {"construct-ally", "undead-ally", "deafened-enemy", "banshee"}
    assert actor.state.resources[0].current_uses == 0
    assert choose_area_save(actor, setup) is None
    assert build_combatant_state(actor.state.template).resources[0].current_uses == 1


def test_sunlight_prohibits_wail_without_spending_resource(monkeypatch):
    actor, living, hero, construct, undead, deafened, setup = _arena()
    selected = choose_area_save(actor, setup)
    assert selected is not None
    monkeypatch.setattr("app.combat.area_save_actions.actor_inside_environment_context",
                        lambda *_: True)
    assert choose_area_save(actor, setup) is None
    with pytest.raises(ValueError, match="prohibited environment"):
        resolve_area_save(1, 1, actor, setup, selected[0], selected[1], FixedDiceProvider([1]))
    assert actor.state.resources[0].current_uses == 1
    assert actor.state.action_available is True

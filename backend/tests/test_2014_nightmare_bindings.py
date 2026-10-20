"""Nightmare source clauses: already-supported Hooves, no rider or planes in Pit."""
from __future__ import annotations

from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_arena_action_policy_2014 import source_proven_ethereal_shift_action_2014
from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.combatants import DamageType
from scripts.browser_template_serializer import template_row


def _nightmare():
    return next(row for row in load_monster_source_2014() if row.id == "nightmare")


def test_mount_only_resistance_and_ethereal_action_are_source_proven_noncombat() -> None:
    source = _nightmare()
    unchanged = source.model_dump_json()
    assert "Confer Fire Resistance" in source.trait_names
    assert "Ethereal Stride" in source.action_names
    assert verified_arena_inert_trait_2014(source, "Confer Fire Resistance")
    assert source_proven_ethereal_shift_action_2014(source, "Ethereal Stride")
    assert basic_blockers_2014(source) == (), (basic_blockers_2014(source), source.source_actions, source.source_traits)
    assert source.model_dump_json() == unchanged


def test_nightmare_keeps_its_own_fire_immunity_without_adding_riders() -> None:
    source = _nightmare()
    template = compile_combatant(adapt_basic_monster_2014(source))
    state = build_combatant_state(template)
    assert DamageType.FIRE in template.damage_immunities
    assert not state.temporary_damage_resistances
    assert not state.timed_effects
    assert not state.concentration
    assert not template.timed_self_buff_actions
    assert "Confer Fire Resistance" in template.source_trait_names
    assert template.weapon_attack.weapon.name == "Hooves"
    assert template_row(template)["kind"] == "monster"


def test_changed_rider_resistance_source_cannot_be_silently_excluded() -> None:
    original = _nightmare()
    changed = original.model_copy(update={
        "source_traits": (original.source_traits or "").replace(
            "to anyone riding it.", "to any ally in the arena."
        )
    })
    assert changed.source_traits != original.source_traits
    assert not verified_arena_inert_trait_2014(changed, "Confer Fire Resistance")
    assert "source:trait" in basic_blockers_2014(changed)


def test_added_ethereal_combat_rider_stays_blocked() -> None:
    original = _nightmare()
    changed = original.model_copy(update={
        "source_actions": (original.source_actions or "").replace(
            "or vice versa.", "or vice versa, and enemies take 4d6 fire damage."
        )
    })
    assert changed.source_actions != original.source_actions
    assert not source_proven_ethereal_shift_action_2014(changed, "Ethereal Stride")
    assert "source:extra-action" in basic_blockers_2014(changed)

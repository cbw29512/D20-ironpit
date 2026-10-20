"""Source-only Invisible Stalker admission uses the existing condition engine."""
from __future__ import annotations

from app.combat.conditions import attack_roll_condition_sources
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_innate_conditions_2014 import innate_condition_ids_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014


def _stalker():
    return next(monster for monster in load_monster_source_2014() if monster.id == "invisible-stalker")


def test_2014_source_binds_permanent_invisible_with_source_proven_inert_tracking() -> None:
    monster = _stalker()
    original = monster.model_dump_json()
    assert monster.trait_names == ["Invisibility", "Faultless Tracker"], monster.trait_names
    assert innate_condition_ids_2014(monster) == ["invisible"], monster.source_traits
    assert verified_arena_inert_trait_2014(monster, "Faultless Tracker"), monster.source_traits
    assert basic_blockers_2014(monster) == (), (basic_blockers_2014(monster), monster.source_traits)
    template = compile_combatant(adapt_basic_monster_2014(monster))
    assert template.innate_condition_ids == ["invisible"]
    assert len(template.alternate_weapon_attacks) + 1 >= 1
    assert monster.model_dump_json() == original


def test_invisible_is_present_at_fight_entry_and_survives_normal_slam() -> None:
    monster = _stalker()
    template = compile_combatant(adapt_basic_monster_2014(monster))
    state = build_combatant_state(template)
    assert "invisible" in state.active_effect_ids
    assert state.concentration is None
    assert not state.timed_effects
    assert all(not getattr(effect, "ends_on_owner_attack", False) for effect in state.timed_effects)
    assert "invisible" in build_combatant_state(template).active_effect_ids


def test_source_mutations_fail_closed_and_do_not_grant_false_invisibility() -> None:
    monster = _stalker()
    sections = source_sections_2014(monster.source_traits)
    assert "Invisibility" in sections, (sections, monster.source_traits)
    mutated = monster.model_copy(update={
        "source_traits": (monster.source_traits or "").replace(
            "The stalker is invisible.", "The stalker can become invisible if it takes an Action."
        ),
    })
    assert mutated.source_traits != monster.source_traits
    assert innate_condition_ids_2014(mutated) == []
    assert "source:trait" in basic_blockers_2014(mutated)
    changed_tracker = monster.model_copy(update={
        "source_traits": (monster.source_traits or "").replace(
            "knows the location of its summoner", "knows the exact location of every enemy"
        ),
    })
    assert changed_tracker.source_traits != monster.source_traits
    assert not verified_arena_inert_trait_2014(changed_tracker, "Faultless Tracker")
    assert "source:trait" in basic_blockers_2014(changed_tracker)

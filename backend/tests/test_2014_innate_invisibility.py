"""Innate conditions begin with the fight and cannot expire as ordinary spell buffs."""
from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.combat.condition_removal import remove_condition
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition, remove_effect_group
from app.combat.visibility_rules import can_see
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_innate_conditions_2014 import innate_condition_ids_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.demo import build_demo_fighter
from app.domain.encounters import EncounterCombatant
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def stalker():
    try:
        return next(m for m in load_monster_source_2014() if m.id == "invisible-stalker")
    except Exception:
        logger.exception("Failed to load exact 2014 Invisible Stalker source.")
        raise


def test_innate_invisibility_source_is_a_permanent_shared_condition() -> None:
    source = stalker()
    before = source.model_dump_json()
    assert source.trait_names.count("Invisibility") == 1
    assert innate_condition_ids_2014(source) == ["invisible"]
    assert basic_blockers_2014(source) == ()
    template = compile_combatant(adapt_basic_monster_2014(source))
    assert template.innate_condition_ids == ["invisible"]
    assert template.source_trait_names == source.trait_names
    assert template_row(template)["innate_condition_ids"] == ["invisible"]
    state = build_combatant_state(template)
    ordinary = build_combatant_state(build_demo_fighter())
    assert state.active_effect_ids == ["invisible"]
    assert not state.timed_effects
    assert has_condition(state, "invisible")
    assert not can_see(ordinary, state, 5)
    seer = build_combatant_state(build_demo_fighter().model_copy(update={"truesight_ft": 30}))
    assert can_see(seer, state, 5)
    assert source.model_dump_json() == before


def test_innate_invisibility_cannot_be_deleted_by_timed_expiry_or_cleansing() -> None:
    template = compile_combatant(adapt_basic_monster_2014(stalker()))
    state = build_combatant_state(template)
    apply_timed_condition(state, "invisible", "caster", source_effect_id="temporary-visibility", applied_round=1)
    effect = state.timed_effects[0]
    assert remove_effect_group(state, effect) == []
    assert not state.timed_effects
    assert has_condition(state, "invisible")
    assert state.active_effect_ids.count("invisible") == 1
    member = EncounterCombatant(combatant_id="stalker", side="monsters", position_ft=0, state=state)
    remove_condition(member, "invisible")
    assert has_condition(state, "invisible")
    assert state.active_effect_ids == ["invisible"]
    second = build_combatant_state(template)
    assert second.active_effect_ids == ["invisible"]
    assert not second.timed_effects


def test_innate_condition_binding_fails_closed_without_unconditional_source() -> None:
    source = stalker()
    missing = source.model_copy(update={"source_traits": None})
    assert innate_condition_ids_2014(missing) == []
    assert "source:trait" in basic_blockers_2014(missing)
    conditional = source.model_copy(update={
        "source_traits": (source.source_traits or "").replace("is invisible.", "can become invisible."),
    })
    assert conditional.source_traits != source.source_traits
    assert innate_condition_ids_2014(conditional) == []
    assert "source:trait" in basic_blockers_2014(conditional)

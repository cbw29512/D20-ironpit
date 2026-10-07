from __future__ import annotations

import pytest

from app.combat.instant_death import apply_instant_death, apply_terminal_effect_tag
from app.combat.regeneration import apply_start_of_turn_regeneration
from app.combat.replacement_forms import enter_replacement_form
from app.combat.state import build_combatant_state
from app.combat.zero_hp import restore_hit_points
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.domain.modifiers import CombatModifier, ConcentrationState, ModifierKind
from app.domain.regeneration import RegenerationTrait


def _template():
    try:
        # Changing names proves that the resolver reads semantic data only.
        armor = next(item for item in build_basic_2014_monsters() if item.name == "Animated Armor")
        return armor.model_copy(update={"name": "Unrelated display name"})
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed to build terminal-effect test template.")
        raise


def _prevention():
    return CombatModifier(
        id="protection", source_id="ally", source_effect_id="protection",
        kind=ModifierKind.ZERO_HP_REPLACEMENT, replacement_hp=1,
        prevents_instant_death=True,
    )


def test_terminal_tag_bypasses_prevention_but_ordinary_instant_death_keeps_it():
    terminal = build_combatant_state(_template())
    ordinary = build_combatant_state(_template())
    for state in (terminal, ordinary):
        state.active_modifiers.append(_prevention())
    assert apply_terminal_effect_tag(terminal, " ANTIMAGIC ") == "dead"
    assert terminal.active_modifiers == [_prevention()]
    assert apply_instant_death(ordinary) == "instant_death_prevented"
    assert not ordinary.is_dead


def test_terminal_death_cannot_heal_or_regenerate_and_next_fight_is_fresh():
    template = _template().model_copy(update={
        "regeneration": RegenerationTrait(amount=10, survives_zero_until_turn=True),
    })
    before = template.model_dump()
    state = build_combatant_state(template)
    state.is_unconscious = True
    state.current_hp = 0
    assert apply_terminal_effect_tag(state, "antimagic") == "dead"
    assert apply_terminal_effect_tag(state, "antimagic") == "unchanged"
    assert restore_hit_points(state, 10) == 0
    assert apply_start_of_turn_regeneration(state)[0] == 0
    assert state.current_hp == 0 and state.is_dead
    fresh = build_combatant_state(template)
    assert fresh.current_hp == template.max_hp and not fresh.is_dead
    assert template.model_dump() == before


def test_terminal_death_ends_declared_form_and_concentration_owned_buffs():
    template = _template()
    state, ally = build_combatant_state(template), build_combatant_state(template)
    enter_replacement_form(
        state, source_id="form", source_name="Any form",
        form_template=template.model_copy(update={"id": "other-form"}),
        action_cost="action", ends_on_incapacitated=True,
    )
    state.concentration = ConcentrationState(source_id="owner", effect_id="buff", started_round=1)
    ally.active_modifiers.append(CombatModifier(
        id="buff", source_id="owner", source_effect_id="buff",
        kind=ModifierKind.ARMOR_CLASS, flat_bonus=2, concentration_required=True,
    ))
    assert apply_terminal_effect_tag(state, "antimagic", affected_states=[ally]) == "dead"
    assert state.replacement_form is None and state.template.id == template.id
    assert state.concentration is None and ally.active_modifiers == []
    assert state.current_hp == 0 and state.is_dead


def test_nonmatching_creature_and_invalid_tag_never_apply_terminal_death():
    state = build_combatant_state(_template().model_copy(update={"terminal_effect_tags": []}))
    assert apply_terminal_effect_tag(state, "antimagic") == "not_susceptible"
    with pytest.raises(ValueError, match="non-empty"):
        apply_terminal_effect_tag(state, " ")
    assert not state.is_dead and state.current_hp == state.template.max_hp

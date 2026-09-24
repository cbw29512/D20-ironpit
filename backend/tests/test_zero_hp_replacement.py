from app.combat.defensive_spell_resolution import resolve_defensive_spell
from app.combat.precombat_spells import choose_defensive_spell
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage, reduce_to_zero_hit_points
from app.combat.zero_hp_replacement import (
    consume_instant_death_prevention,
    consume_zero_hp_replacement_log,
)
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.content.paladin_devotion_2014_spells import death_ward_2014
from app.domain.encounters import EncounterCombatant
from app.domain.modifiers import ModifierKind


def _member():
    template = build_aurelia_brightshield_2014(13)
    state = build_combatant_state(template)
    return EncounterCombatant(
        combatant_id="aurelia",
        side="heroes",
        position_ft=0,
        state=state,
    )


def _cast_death_ward(member: EncounterCombatant):
    spell = death_ward_2014()
    resource = next(item for item in member.state.resources if item.id == "spell-slot-4")
    before_action = member.state.action_available
    event = resolve_defensive_spell(
        1,
        member,
        [member],
        spell,
        4,
        resource,
        [member.state],
    )
    assert member.state.action_available is before_action is True
    assert resource.current_uses == 0
    assert member.state.opening_buff_spell_id == "death-ward"
    assert "death-ward" in member.state.active_buff_effect_ids
    modifiers = [
        item for item in member.state.active_modifiers
        if item.source_effect_id == "death-ward"
    ]
    assert len(modifiers) == 1
    assert modifiers[0].kind is ModifierKind.ZERO_HP_REPLACEMENT
    assert modifiers[0].replacement_hp == 1
    assert modifiers[0].prevents_instant_death is True
    assert event.feature_id == "death-ward"
    return modifiers[0]


def test_death_ward_is_preferred_level_13_opening_buff_and_spends_slot_not_action() -> None:
    member = _member()
    choice = choose_defensive_spell(member)
    assert choice is not None
    spell, slot_level, _resource = choice
    assert spell.id == "death-ward"
    assert slot_level == 4
    _cast_death_ward(member)


def test_death_ward_replaces_first_damage_drop_to_zero_then_ends() -> None:
    member = _member()
    _cast_death_ward(member)

    outcome = apply_damage(member.state, member.state.current_hp + member.state.template.max_hp)

    assert outcome == "zero_hp_replacement"
    assert member.state.current_hp == 1
    assert member.state.is_dead is False
    assert member.state.is_unconscious is False
    assert "death-ward" not in member.state.active_buff_effect_ids
    assert all(item.source_effect_id != "death-ward" for item in member.state.active_modifiers)
    assert "Death Ward prevents the drop to 0 HP" in consume_zero_hp_replacement_log(member.state)

    second = apply_damage(member.state, 1)
    assert second == "unconscious"
    assert member.state.current_hp == 0


def test_death_ward_does_not_trigger_on_non_damage_zero_hp_reduction() -> None:
    member = _member()
    _cast_death_ward(member)

    outcome = reduce_to_zero_hit_points(member.state)

    assert outcome == "unconscious"
    assert member.state.current_hp == 0
    assert "death-ward" in member.state.active_buff_effect_ids


def test_death_ward_generic_instant_death_prevention_consumes_same_source_buff() -> None:
    member = _member()
    _cast_death_ward(member)

    assert consume_instant_death_prevention(member.state) is True
    assert "death-ward" not in member.state.active_buff_effect_ids
    assert all(item.source_effect_id != "death-ward" for item in member.state.active_modifiers)
    assert "Death Ward negates an instant-death effect" in consume_zero_hp_replacement_log(member.state)

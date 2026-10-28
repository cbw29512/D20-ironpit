from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import weapon_attack_damage_multiplier
from app.combat.spell_attack_policy import choose_spell_attack
from app.combat.spell_attack_sequence import resolve_spell_attack_sequence
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_spells_2014 import innate_spell_attack_actions_2014
from app.content.monster_innate_support_2014 import innate_alternate_spell_casts_2014, innate_spell_resources_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind


def _source():
    return next(card for card in load_monster_source_2014() if card.id == "night-hag")


def _setup():
    caster = EncounterCombatant(
        combatant_id="night-hag", side="monsters", position_ft=0,
        state=build_combatant_state(compile_combatant(adapt_monster_mechanics_2014(_source()))),
    )
    target_template = build_karnok_stoneward().model_copy(deep=True)
    target_template.armor_class = 10
    target = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=30,
        state=build_combatant_state(target_template),
    )
    return caster, target, EncounterSetup(
        heroes=[target], monsters=[caster], hero_total_levels=20,
        monster_total_cr="5", ruleset="2014",
    )


def test_every_source_row_binds_exact_ray_parameters() -> None:
    applicable = [
        card for card in load_monster_source_2014()
        if any(row.get("id") == "ray-of-enfeeblement" for row in innate_spells_2014(card))
    ]
    assert [card.id for card in applicable] == ["night-hag"]
    row, = [row for row in innate_spells_2014(applicable[0]) if row.get("id") == "ray-of-enfeeblement"]
    assert row == {
        "id": "ray-of-enfeeblement", "name": "ray of enfeeblement",
        "usage": "per_day", "uses_per_day": 2, "shared_pool": False, "qualifier": None,
    }
    action, = innate_spell_attack_actions_2014(applicable[0])
    assert (action.level, action.range_ft, action.attack_bonus) == (2, 60, 6)
    assert action.concentration is True and action.duration_minutes == 1
    modifier, = action.on_hit_modifier_effects
    assert modifier.kind == "weapon-attack-damage-multiplier"
    assert modifier.multiplier == 0.5 and modifier.required_attack_ability == "strength"
    timed, = action.on_hit_timed_effects
    assert (timed.repeat_save_ability, timed.repeat_save_dc, timed.repeat_save_timing) == (
        "constitution", 14, "target_turn_end",
    )
    resource, = [item for item in innate_spell_resources_2014(applicable[0]) if item.id == action.id]
    grant, = [item for item in innate_alternate_spell_casts_2014(applicable[0]) if item.spell_id == action.id]
    assert resource.max_uses == 2
    assert grant.resource_id == action.id and grant.cast_level == 2


def test_ray_casts_from_daily_resource_and_successful_repeat_save_ends_it() -> None:
    caster, target, setup = _setup()
    choice = choose_spell_attack(caster, setup, "1:night-hag")
    assert choice is not None and choice.action.id == "ray-of-enfeeblement"
    assert choice.alternate_cast is not None
    events, _ = resolve_spell_attack_sequence(
        1, 1, caster, target, choice.action, setup, "1:night-hag",
        FixedDiceProvider([15]), slot_level=choice.slot_level,
        alternate_cast=choice.alternate_cast,
    )
    assert events[0].hit is True and events[0].damage_roll is None
    assert caster.state.resources[0].current_uses == 1
    assert caster.state.concentration is not None
    assert target.state.timed_effects[0].repeat_save_dc == 14
    assert weapon_attack_damage_multiplier(target.state, target.state.template.weapon_attack) == 0.5

    save_events, _ = resolve_target_condition_timing(
        2, 1, target, "target_turn_end", FixedDiceProvider([20]), setup,
    )
    assert save_events[0].save_succeeded is True
    assert caster.state.concentration is None
    assert target.state.timed_effects == []
    assert target.state.active_modifiers == []


def test_identical_ray_modifiers_do_not_stack_but_distinct_effects_do() -> None:
    _, target, _ = _setup()
    attack = target.state.template.weapon_attack
    assert attack is not None
    base = dict(
        source_effect_id="ray-of-enfeeblement", source_name="Ray of Enfeeblement",
        source_is_magical=True, kind=ModifierKind.WEAPON_ATTACK_DAMAGE_MULTIPLIER,
        multiplier=0.5, required_attack_ability="strength", concentration_required=True,
    )
    target.state.active_modifiers = [
        CombatModifier(id="ray-a", source_id="a", **base),
        CombatModifier(id="ray-b", source_id="b", **base),
    ]
    assert weapon_attack_damage_multiplier(target.state, attack) == 0.5
    target.state.active_modifiers.append(CombatModifier(
        id="distinct", source_id="c", **{**base, "source_effect_id": "distinct-weakness"},
    ))
    assert weapon_attack_damage_multiplier(target.state, attack) == 0.25

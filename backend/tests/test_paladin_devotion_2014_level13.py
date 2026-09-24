from app.combat.modifier_stack import add_modifier
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.combat.zero_hp_replacement import (
    consume_instant_death_prevention,
    consume_zero_hp_replacement_log,
)
from app.content.paladin_2014_spell_package import build_paladin_2014_spell_package
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.modifiers import CombatModifier, ModifierKind


def test_zero_hp_replacement_consumes_source_owned_buff_once() -> None:
    template = build_aurelia_brightshield_2014(13)
    state = build_combatant_state(template)
    state.current_hp = 5
    state.active_buff_effect_ids.append("death-ward")
    add_modifier(state, CombatModifier(
        id="caster:death-ward:target:0",
        source_id="caster",
        source_effect_id="death-ward",
        source_name="Death Ward",
        source_is_magical=True,
        kind=ModifierKind.ZERO_HP_REPLACEMENT,
        replacement_hp=1,
        prevents_instant_death=True,
    ))

    outcome = apply_damage(state, 20)

    assert outcome == "zero_hp_replacement"
    assert state.current_hp == 1
    assert state.is_alive is True
    assert state.is_dead is False
    assert state.is_unconscious is False
    assert "death-ward" not in state.active_buff_effect_ids
    assert not any(item.source_effect_id == "death-ward" for item in state.active_modifiers)
    assert "Death Ward prevents the drop to 0 HP" in consume_zero_hp_replacement_log(state)

    second = apply_damage(state, 5)
    assert second == "unconscious"
    assert state.current_hp == 0


def test_zero_hp_replacement_can_negate_future_non_damage_instant_death() -> None:
    state = build_combatant_state(build_aurelia_brightshield_2014(13))
    state.active_buff_effect_ids.append("death-ward")
    add_modifier(state, CombatModifier(
        id="caster:death-ward:target:0",
        source_id="caster",
        source_effect_id="death-ward",
        source_name="Death Ward",
        source_is_magical=True,
        kind=ModifierKind.ZERO_HP_REPLACEMENT,
        replacement_hp=1,
        prevents_instant_death=True,
    ))

    assert consume_instant_death_prevention(state) is True
    assert not any(item.source_effect_id == "death-ward" for item in state.active_modifiers)
    assert "Death Ward negates an instant-death effect" in consume_zero_hp_replacement_log(state)


def test_paladin_level_13_uses_non_summoning_combat_replacement() -> None:
    hero = build_aurelia_brightshield_2014(13)
    profile = build_aurelia_brightshield_2014_profile(13)
    package = build_paladin_2014_spell_package(13, hero.ability_scores.modifier("charisma"))

    assert {item.id: item.max_uses for item in hero.resources if item.id.startswith("spell-slot-")} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
    }
    defense_ids = {item.id for item in hero.defensive_spell_actions}
    assert {"death-ward", "freedom-of-movement"} <= defense_ids

    assert package is not None
    prepared_ids = {item.id for item in package.spells}
    assert "death-ward" in prepared_ids
    assert "purify-food-and-drink" not in prepared_ids
    guardian = next(item for item in package.always_prepared_spells if item.id == "guardian-of-faith")
    assert guardian.required_capabilities == ["arena-unavailable-summon"]

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["death-ward"].automated is True
    assert audits["guardian-of-faith"].combat_relevant is False
    assert audits["guardian-of-faith"].automated is False

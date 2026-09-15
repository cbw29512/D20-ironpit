from __future__ import annotations

from app.combat.spell_modifiers import apply_spell_modifiers
from app.content.monster_catalog_2014 import monster_by_id_2014
from app.domain.runtime import CombatantState


def test_archmage_fire_shield_compiles_as_real_defensive_spell() -> None:
    archmage = monster_by_id_2014("archmage")
    shields = {spell.id: spell for spell in archmage.defensive_spell_actions}

    assert set(shields) == {"fire-shield-warm", "fire-shield-chill"}
    warm = shields["fire-shield-warm"]
    assert warm.level == 4
    assert warm.damage_resistances == ["cold"]
    assert warm.modifier_effects[0].kind == "adjacent-melee-hit-reactive-damage"
    assert warm.modifier_effects[0].dice_count == 2
    assert warm.modifier_effects[0].dice_size == 8
    assert warm.modifier_effects[0].damage_type == "fire"


def test_fire_shield_reactive_effect_installs_on_combat_state() -> None:
    archmage = monster_by_id_2014("archmage")
    warm = next(spell for spell in archmage.defensive_spell_actions if spell.id == "fire-shield-warm")
    state = CombatantState(template=archmage, current_hp=archmage.max_hp)

    apply_spell_modifiers(state, [(archmage.id, state)], archmage.id, warm, 0, [state])

    assert len(state.temporary_melee_hit_reactive_damage) == 1
    rule = state.temporary_melee_hit_reactive_damage[0]
    assert rule.range_ft == 5
    assert rule.dice_count == 2
    assert rule.dice_size == 8
    assert rule.damage_type.value == "fire"

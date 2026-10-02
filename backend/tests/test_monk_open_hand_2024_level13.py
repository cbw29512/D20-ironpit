from __future__ import annotations

from app.combat.attack_damage_reduction import apply_attack_damage_reduction, can_reduce_attack_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.certified_heroes import build_certified_hero_registry
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.models import DamageRollComponent, DamageType


def _fire_component(total: int = 8) -> DamageRollComponent:
    return DamageRollComponent(
        source="test-fire",
        notation=str(total),
        rolls=[],
        modifier=total,
        damage_type=DamageType.FIRE,
        total=total,
    )


def test_2024_open_hand_monk_level13_advances_pb_focus_and_derived_stats() -> None:
    template = build_kael_stillwater_2024(13)
    profile = build_kael_stillwater_2024_profile(13)
    fingerprint = build_kael_2024_combat_profiles(13)[-1]

    assert template.level == profile.level == fingerprint.level == 13
    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (16, 107, 50, 10)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (16, 107, 50, 10)
    assert template.weapon_attack.attack_bonus == 10
    assert template.weapon_attack.damage_bonus == 5
    assert template.saving_throw_bonuses["dexterity"] == 10
    assert template.skill_bonuses["acrobatics"] == 10
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 13

    stunning = template.progression_features.resource_backed_on_hit_save_rider
    assert stunning is not None
    assert stunning.save_dc == 14


def test_2024_open_hand_monk_level13_deflect_energy_widens_existing_reaction() -> None:
    level12 = build_kael_stillwater_2024(12)
    level13 = build_kael_stillwater_2024(13)
    state12 = build_combatant_state(level12)
    state13 = build_combatant_state(level13)
    component = _fire_component()

    assert level12.attack_damage_reduction_reaction is not None
    assert level13.attack_damage_reduction_reaction is not None
    assert {item.value for item in level12.attack_damage_reduction_reaction.required_damage_types} == {
        "bludgeoning", "piercing", "slashing",
    }
    assert level13.attack_damage_reduction_reaction.required_damage_types == []
    assert can_reduce_attack_damage(state12, level12.weapon_attack, [component]) is False
    assert can_reduce_attack_damage(state13, level13.weapon_attack, [component]) is True

    result = apply_attack_damage_reduction(
        state13,
        level13.weapon_attack,
        [component],
        FixedDiceProvider([10]),
    )
    assert result.used is True
    assert result.source_id == "deflect-attacks"
    assert result.zeroed_attack is True
    assert result.components[0].total == 0
    assert state13.reaction_available is False


def test_2024_open_hand_monk_level13_redirect_and_audit_are_certified() -> None:
    template = build_kael_stillwater_2024(13)
    profile = build_kael_stillwater_2024_profile(13)
    audits = {item.feature_id: item for item in profile.feature_audits}

    reaction = template.attack_damage_reduction_reaction
    assert reaction is not None
    redirect = reaction.zero_damage_redirect
    assert redirect is not None
    assert redirect.resource_id == "focus-points"
    assert redirect.resource_cost == 1
    assert redirect.melee_range_ft == 5
    assert redirect.ranged_range_ft == 60
    assert redirect.save_ability == "dexterity"
    assert redirect.save_dc == 14
    assert (redirect.damage_dice_count, redirect.damage_dice_size) == (2, 10)
    assert redirect.damage_bonus_ability == "dexterity"

    assert audits["deflect-energy"].automated is True
    assert "any damage type" in (audits["deflect-energy"].notes or "")

    registry = build_certified_hero_registry()
    assert registry[("monk", 13, "canonical")] == ("Kael Stillwater", "kael-stillwater-l13")

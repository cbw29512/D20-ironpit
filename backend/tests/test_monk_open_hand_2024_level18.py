from __future__ import annotations

from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.source_bound_effects import cleanup_disabled_source_effects
from app.combat.start_turn_timed_self_buffs import resolve_start_turn_timed_self_buff
from app.combat.state import begin_turn, build_combatant_state
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    monk = EncounterCombatant(
        combatant_id="hero-1:kael-l18",
        side="heroes",
        position_ft=5,
        state=build_combatant_state(build_kael_stillwater_2024(18)),
    )
    target = EncounterCombatant(
        combatant_id="monster-1:target",
        side="monsters",
        position_ft=10,
        state=build_combatant_state(build_karnok_stoneward_level(1)),
    )
    setup = EncounterSetup(
        heroes=[monk],
        monsters=[target],
        hero_total_levels=18,
        monster_total_cr="0",
        ruleset="2024",
    )
    return monk, target, setup


def test_2024_open_hand_monk_level18_snapshot_and_superior_defense_binding() -> None:
    template = build_kael_stillwater_2024(18)
    profile = build_kael_stillwater_2024_profile(18)
    fingerprint = build_kael_2024_combat_profiles(18)[-1]

    assert template.level == profile.level == fingerprint.level == 18
    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (17, 147, 60, 11)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (17, 147, 60, 11)
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 18

    assert len(template.timed_self_buff_actions) == 1
    action = template.timed_self_buff_actions[0]
    assert action.id == "superior-defense"
    assert action.activation_timing == "start_turn"
    assert (action.resource_id, action.resource_cost) == ("focus-points", 3)
    assert action.duration_rounds == 10
    assert action.ends_if_source_incapacitated is True
    assert set(action.damage_resistances) == {item for item in DamageType if item != DamageType.FORCE}
    assert DamageType.FORCE not in action.damage_resistances

    audit = next(item for item in profile.feature_audits if item.feature_id == "superior-defense")
    assert audit.combat_relevant is True
    assert audit.automated is True

    registry = build_certified_hero_registry()
    assert registry[("monk", 18, "canonical")] == ("Kael Stillwater", "kael-stillwater-l18")


def test_superior_defense_activates_at_turn_start_without_spending_action_economy() -> None:
    monk, _, setup = _setup()
    begin_turn(monk.state)
    before_action = monk.state.action_available
    before_bonus = monk.state.bonus_action_available

    event = resolve_start_turn_timed_self_buff(1, 1, monk, setup)

    assert event is not None
    assert event.feature_id == "superior-defense"
    assert event.resource_remaining == 15
    assert monk.state.action_available is before_action is True
    assert monk.state.bonus_action_available is before_bonus is True
    effect = next(item for item in monk.state.timed_effects if item.source_effect_id == "superior-defense")
    assert effect.expires_round == 11
    assert effect.expiry_timing == "source_turn_start"
    assert adjusted_damage_amount(9, DamageType.FIRE, monk.state) == 4
    assert adjusted_damage_amount(9, DamageType.PSYCHIC, monk.state) == 4
    assert adjusted_damage_amount(9, DamageType.FORCE, monk.state) == 9


def test_superior_defense_does_not_reactivate_and_ends_if_monk_is_incapacitated() -> None:
    monk, _, setup = _setup()
    begin_turn(monk.state)

    first = resolve_start_turn_timed_self_buff(1, 1, monk, setup)
    assert first is not None
    assert resolve_start_turn_timed_self_buff(2, 2, monk, setup) is None

    monk.state.active_effect_ids.append("incapacitated")
    cleanup_disabled_source_effects(setup)

    assert not any(item.source_effect_id == "superior-defense" for item in monk.state.timed_effects)
    assert adjusted_damage_amount(9, DamageType.FIRE, monk.state) == 9


def test_superior_defense_requires_three_focus_points() -> None:
    monk, _, setup = _setup()
    begin_turn(monk.state)
    focus = next(item for item in monk.state.resources if item.id == "focus-points")
    focus.current_uses = 2

    assert resolve_start_turn_timed_self_buff(1, 1, monk, setup) is None
    assert focus.current_uses == 2
    assert monk.state.action_available is True
    assert monk.state.bonus_action_available is True

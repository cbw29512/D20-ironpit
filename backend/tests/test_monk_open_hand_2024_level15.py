from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.initiative_resource_refill import resolve_initiative_resource_refills
from app.combat.state import build_combatant_state
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup() -> tuple[EncounterCombatant, EncounterSetup]:
    hero = EncounterCombatant(
        combatant_id="kael-15",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_kael_stillwater_2024(15)),
    )
    target = EncounterCombatant(
        combatant_id="target",
        side="monsters",
        position_ft=5,
        state=build_combatant_state(build_karnok_stoneward_level(1)),
    )
    return hero, EncounterSetup(
        heroes=[hero],
        monsters=[target],
        hero_total_levels=15,
        monster_total_cr="0",
        ruleset="2024",
    )


def _resource(member: EncounterCombatant, resource_id: str):
    return next(item for item in member.state.resources if item.id == resource_id)


def test_2024_open_hand_monk_level15_advances_hp_focus_and_registry() -> None:
    template = build_kael_stillwater_2024(15)
    profile = build_kael_stillwater_2024_profile(15)
    fingerprint = build_kael_2024_combat_profiles(15)[-1]

    assert template.level == profile.level == fingerprint.level == 15
    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (16, 123, 55, 10)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (16, 123, 55, 10)
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 15
    assert fingerprint.save_proficiencies == (
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
    )

    registry = build_certified_hero_registry()
    assert registry[("monk", 15, "canonical")] == ("Kael Stillwater", "kael-stillwater-l15")


def test_2024_perfect_focus_waits_when_uncanny_metabolism_is_used() -> None:
    hero, setup = _setup()
    _resource(hero, "focus-points").current_uses = 2
    _resource(hero, "uncanny-metabolism").current_uses = 1
    hero.state.current_hp -= 10

    events, sequence = resolve_initiative_resource_refills(1, setup, FixedDiceProvider([5]))

    assert sequence == 2
    assert [event.feature_id for event in events] == ["uncanny-metabolism"]
    assert _resource(hero, "focus-points").current_uses == 15
    assert _resource(hero, "uncanny-metabolism").current_uses == 0


def test_2024_perfect_focus_restores_to_four_when_uncanny_is_not_used() -> None:
    hero, setup = _setup()
    _resource(hero, "focus-points").current_uses = 2
    _resource(hero, "uncanny-metabolism").current_uses = 0

    events, sequence = resolve_initiative_resource_refills(7, setup)

    assert sequence == 8
    assert [event.feature_id for event in events] == ["perfect-focus"]
    assert _resource(hero, "focus-points").current_uses == 4
    assert events[0].resource_remaining == 4


def test_2024_perfect_focus_does_not_trigger_at_four_focus() -> None:
    hero, setup = _setup()
    _resource(hero, "focus-points").current_uses = 4
    _resource(hero, "uncanny-metabolism").current_uses = 0

    events, sequence = resolve_initiative_resource_refills(3, setup)

    assert events == []
    assert sequence == 3
    assert _resource(hero, "focus-points").current_uses == 4


def test_2024_perfect_focus_audit_is_automated() -> None:
    profile = build_kael_stillwater_2024_profile(15)
    audits = {item.feature_id: item for item in profile.feature_audits}
    perfect = audits["perfect-focus"]

    assert perfect.combat_relevant is True
    assert perfect.automated is True
    assert "Uncanny Metabolism resolves first" in (perfect.notes or "")

from __future__ import annotations

from app.combat.barbarian import (
    end_rage_if_incapacitated,
    enter_rage,
    maintain_rage_with_bonus_action,
    rage_active,
)
from app.combat.initiative_resource_refill import resolve_initiative_resource_refills
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.barbarian_berserker_2014_runtime import build_rokhan_stonefury_2014
from app.content.barbarian_persistent_rage_profile import build_rokhan_stonefury_level15_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template.model_copy(deep=True)),
    )


def _resource(member: EncounterCombatant, resource_id: str):
    try:
        return next(item for item in member.state.resources if item.id == resource_id)
    except StopIteration as exc:
        raise AssertionError(f"Missing resource {resource_id}.") from exc


def _setup(hero: EncounterCombatant) -> EncounterSetup:
    target = _member(build_karnok_stoneward(), "monster:target", "monsters", 5)
    return EncounterSetup(
        heroes=[hero],
        monsters=[target],
        hero_total_levels=15,
        monster_total_cr="0",
        ruleset="2024",
    )


def test_level15_profile_binds_persistent_rage_to_shared_primitives() -> None:
    profile = build_rokhan_stonefury_level15_profile()
    template = build_rokhan_stonefury_level(15)
    grant = template.initiative_resource_refill_grants[0]

    assert profile.level == 15
    assert profile.subclass_id == "path-berserker"
    assert template.progression_features.rage_persists_without_maintenance is True
    assert grant.source_id == "persistent-rage"
    assert grant.source_name == "Persistent Rage"
    assert grant.resource_id == "rage"
    assert grant.when_at_or_below == 4
    assert grant.restore_amount == 5
    assert ("barbarian", 15, "canonical") in build_certified_hero_registry()

    level14 = build_rokhan_stonefury_level(14)
    assert level14.progression_features.rage_persists_without_maintenance is False
    assert level14.initiative_resource_refill_grants == []


def test_persistent_rage_refills_all_expended_rages_when_initiative_is_rolled() -> None:
    hero = _member(build_rokhan_stonefury_level(15), "hero:rokhan-l15", "heroes", 0)
    rage = _resource(hero, "rage")
    rage.current_uses = 2

    events, sequence = resolve_initiative_resource_refills(1, _setup(hero))

    assert sequence == 2
    assert rage.current_uses == 5
    assert len(events) == 1
    assert events[0].feature_id == "persistent-rage"
    assert events[0].resource_remaining == 5

    rage.current_uses = 4
    events, _ = resolve_initiative_resource_refills(7, _setup(hero))
    assert rage.current_uses == 5
    assert len(events) == 1

    events, sequence = resolve_initiative_resource_refills(9, _setup(hero))
    assert events == []
    assert sequence == 9


def test_persistent_rage_uses_full_2024_duration_without_maintenance() -> None:
    hero = _member(build_rokhan_stonefury_level(15), "hero:rokhan-l15", "heroes", 0)
    state = hero.state

    event = enter_rage(1, 1, state, hero.combatant_id)

    assert event is not None
    assert state.rage_max_round == 101
    assert state.rage_expires_round == 101
    state.bonus_action_available = True
    assert maintain_rage_with_bonus_action(2, 2, state, hero.combatant_id) is None
    assert state.bonus_action_available is True


def test_persistent_rage_ignores_stunned_but_ends_on_unconscious_or_heavy_armor() -> None:
    hero = _member(build_rokhan_stonefury_level(15), "hero:rokhan-l15", "heroes", 0)
    state = hero.state
    assert enter_rage(1, 1, state, hero.combatant_id) is not None

    state.active_effect_ids.append("stunned")
    end_rage_if_incapacitated(state)
    assert rage_active(state) is True

    state.is_unconscious = True
    end_rage_if_incapacitated(state)
    assert rage_active(state) is False

    armor_state = build_combatant_state(build_rokhan_stonefury_level(15).model_copy(deep=True))
    assert enter_rage(1, 1, armor_state, "hero:armor") is not None
    armor_state.template.wearing_heavy_armor = True
    end_rage_if_incapacitated(armor_state)
    assert rage_active(armor_state) is False


def test_2014_persistent_rage_keeps_its_existing_lifecycle() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(15))

    assert enter_rage(1, 1, state, "hero:2014") is not None
    assert state.rage_max_round == 11
    assert state.rage_expires_round == 11
    assert state.template.progression_features.rage_persists_without_maintenance is False
    assert state.template.progression_features.persistent_rage_2014 is True

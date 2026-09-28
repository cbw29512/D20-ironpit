from __future__ import annotations

from app.combat.miss_to_hit_override import apply_miss_to_hit_override
from app.combat.state import begin_turn, build_combatant_state
from app.content.fighter_finish_profile import (
    build_karnok_stoneward_level19_profile,
    build_karnok_stoneward_level20_profile,
)
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.certified_heroes import build_certified_hero_registry


def _resource(state, resource_id: str):
    try:
        return next(item for item in state.resources if item.id == resource_id)
    except StopIteration as exc:
        raise AssertionError(f"Missing resource {resource_id}.") from exc


def test_fighter19_combat_prowess_reuses_miss_override_and_turn_refill() -> None:
    profile = build_karnok_stoneward_level19_profile()
    template = build_karnok_stoneward_level(19)
    features = template.progression_features

    assert profile.level == 19
    assert profile.final_ability_scores.dexterity == 18
    assert features.miss_to_hit_override_resource_id == "boon-combat-prowess"
    assert features.miss_to_hit_override_source_name == "Boon of Combat Prowess"
    assert features.start_turn_resource_refill_ids == ["boon-combat-prowess"]
    assert {item.id: item.max_uses for item in template.resources}["boon-combat-prowess"] == 1
    assert ("fighter", 19, "canonical") in build_certified_hero_registry()

    state = build_combatant_state(template)
    converted, feature_id, source_name = apply_miss_to_hit_override(state, hit=False)
    assert converted is True
    assert feature_id == "boon-combat-prowess"
    assert source_name == "Boon of Combat Prowess"
    assert _resource(state, "boon-combat-prowess").current_uses == 0

    converted_again, _, _ = apply_miss_to_hit_override(state, hit=False)
    assert converted_again is False

    begin_turn(state)
    assert _resource(state, "boon-combat-prowess").current_uses == 1


def test_fighter20_uses_four_attack_slots_without_new_resolver() -> None:
    profile = build_karnok_stoneward_level20_profile()
    template = build_karnok_stoneward_level(20)

    assert profile.level == 20
    assert template.max_hp == 224
    assert template.attack_action is not None
    assert len(template.attack_action.slots) == 4
    assert all(
        slot.attack_ids == ["karnok-greatsword", "karnok-shortbow"]
        for slot in template.attack_action.slots
    )
    assert template.progression_features.miss_to_hit_override_resource_id == "boon-combat-prowess"
    assert ("fighter", 20, "canonical") in build_certified_hero_registry()

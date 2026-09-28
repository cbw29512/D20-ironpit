from __future__ import annotations

from app.combat.miss_to_hit_override import apply_miss_to_hit_override
from app.combat.state import begin_turn, build_combatant_state
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_level19_profile import build_karnok_stoneward_level19_profile
from app.content.fighter_progression import build_karnok_stoneward_level


def test_fighter19_combat_prowess_binds_existing_miss_override() -> None:
    try:
        profile = build_karnok_stoneward_level19_profile()
        template = build_karnok_stoneward_level(19)
        features = template.progression_features

        assert profile.level == 19
        assert template.ability_scores is not None
        assert template.ability_scores.dexterity == 18
        assert template.max_hp == 213
        assert features.miss_to_hit_override_resource_id == "boon-combat-prowess"
        assert features.miss_to_hit_override_source_name == "Boon of Combat Prowess"
        assert features.turn_start_resource_refill_ids == ["boon-combat-prowess"]
        assert {item.id: item.max_uses for item in template.resources}["boon-combat-prowess"] == 1
        assert ("fighter", 19, "canonical") in build_certified_hero_registry()
    except Exception as exc:
        raise AssertionError("Fighter 19 Combat Prowess binding failed.") from exc


def test_fighter19_peerless_aim_spends_once_then_refreshes_next_turn() -> None:
    try:
        state = build_combatant_state(build_karnok_stoneward_level(19))
        resource = next(item for item in state.resources if item.id == "boon-combat-prowess")

        hit, feature_id, source_name = apply_miss_to_hit_override(state, hit=False)
        assert (hit, feature_id, source_name) == (
            True,
            "boon-combat-prowess",
            "Boon of Combat Prowess",
        )
        assert resource.current_uses == 0

        hit_again, feature_again, source_again = apply_miss_to_hit_override(state, hit=False)
        assert (hit_again, feature_again, source_again) == (False, None, None)

        begin_turn(state)
        assert resource.current_uses == 1

        hit_next, feature_next, source_next = apply_miss_to_hit_override(state, hit=False)
        assert (hit_next, feature_next, source_next) == (
            True,
            "boon-combat-prowess",
            "Boon of Combat Prowess",
        )
    except Exception as exc:
        raise AssertionError("Fighter 19 Peerless Aim turn refresh failed.") from exc

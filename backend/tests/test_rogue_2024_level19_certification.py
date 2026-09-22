from __future__ import annotations

from app.combat.miss_to_hit_override import apply_miss_to_hit_override
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level19_combat_profile
from app.content.rogue_final_progression_profile import build_mara_quickstep_level19_profile


def _resource(state, resource_id: str):
    return next(item for item in state.resources if item.id == resource_id)


def test_2024_rogue_level19_composes_combat_prowess_from_universal_primitives() -> None:
    level18 = build_mara_quickstep_level(18)
    template = build_mara_quickstep_level(19)

    assert unsupported_mara_rogue_features(19) == ()
    assert template.level == 19
    assert template.max_hp == 193
    assert template.max_hp - level18.max_hp == 10
    assert template.ability_scores is not None
    assert template.ability_scores.strength == 14
    assert template.saving_throw_bonuses["strength"] == 2
    assert template.skill_bonuses["athletics"] == 8
    assert template.progression_features.sneak_attack_d6 == 10
    assert template.progression_features.miss_to_hit_override_resource_id == "boon-combat-prowess"
    assert template.progression_features.miss_to_hit_override_source_name == "Boon of Combat Prowess"
    assert template.progression_features.start_of_turn_resource_refresh_ids == ["boon-combat-prowess"]
    assert {item.id: item.max_uses for item in template.resources}["boon-combat-prowess"] == 1


def test_combat_prowess_refreshes_once_at_each_start_of_turn() -> None:
    state = build_combatant_state(build_mara_quickstep_level(19))
    resource = _resource(state, "boon-combat-prowess")

    hit, feature_id, source_name = apply_miss_to_hit_override(state, hit=False)
    assert (hit, feature_id, source_name) == (
        True, "boon-combat-prowess", "Boon of Combat Prowess",
    )
    assert resource.current_uses == 0

    second = apply_miss_to_hit_override(state, hit=False)
    assert second == (False, None, None)

    begin_turn(state)
    assert resource.current_uses == 1

    refreshed = apply_miss_to_hit_override(state, hit=False)
    assert refreshed[0] is True
    assert resource.current_uses == 0


def test_2024_rogue_level19_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level19_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert profile.level == 19
    assert profile.final_ability_scores.strength == 14
    assert audits["boon-combat-prowess"].automated is True
    assert "generic start-of-turn resource lifecycle" in (audits["boon-combat-prowess"].notes or "")

    fingerprint = build_mara_quickstep_level19_combat_profile()
    assert fingerprint.abilities.strength == 14
    assert fingerprint.max_hp == 193
    assert fingerprint.sneak_attack_d6 == 10
    assert ("boon-combat-prowess", 1) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 19, "canonical")] == ("Mara Quickstep", "mara-quickstep-l19")

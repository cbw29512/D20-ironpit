from __future__ import annotations

from app.combat.miss_to_hit_override import apply_miss_to_hit_override
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level, mara_rogue_features, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level19_combat_profile
from app.content.rogue_final_progression_profile import build_mara_quickstep_level19_profile


def test_2024_rogue_level19_applies_combat_prowess_and_sneak_attack_scaling() -> None:
    level18 = build_mara_quickstep_level(18)
    template = build_mara_quickstep_level(19)

    assert unsupported_mara_rogue_features(19) == ()
    assert "boon-combat-prowess" in mara_rogue_features(19)
    assert template.level == 19
    assert template.ability_scores is not None
    assert template.ability_scores.strength == 14
    assert template.max_hp == 193
    assert template.max_hp - level18.max_hp == 10
    assert template.skill_bonuses["athletics"] == 8
    assert template.progression_features.sneak_attack_d6 == 10

    grants = template.progression_features.miss_to_hit_override_grants
    assert len(grants) == 1
    assert grants[0].source_id == "boon-combat-prowess"
    assert grants[0].source_name == "Boon of Combat Prowess"
    assert grants[0].usage_policy == "refresh_at_turn_start"
    assert grants[0].resource_id is None


def test_2024_rogue_level19_combat_prowess_refreshes_at_own_turn_start() -> None:
    state = build_combatant_state(build_mara_quickstep_level(19))

    assert apply_miss_to_hit_override(state, hit=False) == (
        True, "boon-combat-prowess", "Boon of Combat Prowess",
    )
    assert apply_miss_to_hit_override(state, hit=False) == (False, None, None)

    begin_turn(state)

    assert apply_miss_to_hit_override(state, hit=False) == (
        True, "boon-combat-prowess", "Boon of Combat Prowess",
    )


def test_2024_rogue_level19_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level19_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}
    boon = audits["boon-combat-prowess"]

    assert profile.level == 19
    assert profile.final_ability_scores.strength == 14
    assert profile.ability_score_maximums["strength"] == 30
    assert boon.feature_name == "Boon of Combat Prowess"
    assert boon.combat_relevant is True
    assert boon.automated is True
    assert "universal source-tagged miss-to-hit override" in (boon.notes or "")

    fingerprint = build_mara_quickstep_level19_combat_profile()
    assert fingerprint.abilities.strength == 14
    assert ("athletics", 8) in fingerprint.skill_bonuses
    assert fingerprint.max_hp == 193
    assert fingerprint.sneak_attack_d6 == 10

    registry = build_certified_hero_registry()
    assert registry[("rogue", 19, "canonical")] == ("Mara Quickstep", "mara-quickstep-l19")

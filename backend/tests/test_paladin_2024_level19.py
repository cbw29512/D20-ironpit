from __future__ import annotations

import logging

from app.combat.miss_to_hit_override import apply_miss_to_hit_override
from app.combat.state import begin_turn, build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats

logger = logging.getLogger(__name__)


def _resource(state, resource_id: str):
    try:
        return next(item for item in state.resources if item.id == resource_id)
    except StopIteration as exc:
        raise AssertionError(f"Missing resource {resource_id}.") from exc


def test_level_nineteen_reuses_combat_prowess_and_advances_paladin_spellcasting() -> None:
    try:
        hero = build_aurelia_brightshield_2024(19)
        previous = build_aurelia_brightshield_2024(18)
        profile = build_aurelia_brightshield_2024_profile(19)

        assert hero.name == previous.name
        assert hero.level == 19
        assert profile.final_ability_scores is not None
        assert profile.final_ability_scores.charisma == 20
        assert profile.final_ability_scores.strength == 20
        assert hero.max_hp == 156
        assert hero.weapon_attack.attack_bonus == 11
        assert hero.skill_bonuses["persuasion"] == 11

        protection = hero.progression_features.friendly_saving_throw_aura
        assert protection is not None
        assert protection.radius_ft == 30
        assert protection.flat_bonus == 5

        assert hero.progression_features.miss_to_hit_override_resource_id == "boon-combat-prowess"
        assert hero.progression_features.miss_to_hit_override_source_name == "Boon of Combat Prowess"
        assert hero.progression_features.start_turn_resource_refill_ids == ["boon-combat-prowess"]

        resources = {item.id: item.max_uses for item in hero.resources}
        assert resources["lay-on-hands"] == 95
        assert resources["spell-slot-5"] == 2
        assert resources["boon-combat-prowess"] == 1

        state = build_combatant_state(hero)
        converted, feature_id, source_name = apply_miss_to_hit_override(state, hit=False)
        assert converted is True
        assert feature_id == "boon-combat-prowess"
        assert source_name == "Boon of Combat Prowess"
        assert _resource(state, "boon-combat-prowess").current_uses == 0
        assert apply_miss_to_hit_override(state, hit=False)[0] is False
        begin_turn(state)
        assert _resource(state, "boon-combat-prowess").current_uses == 1

        package = canonical_spell_package("paladin", 19, "2024")
        assert package is not None
        assert len(package.spells) == 15
        assert package.spells[-1].id == "banishing-smite"
        assert package.spells[-1].role == "damage"
        assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]

        flame_strike = next(item for item in hero.spell_save_actions if item.id == "flame-strike")
        assert flame_strike.dc == 19

        audits = {item.feature_id: item for item in profile.feature_audits}
        assert audits["boon-combat-prowess"].automated is True
        assert audits["banishing-smite"].automated is False

        fingerprint = next(item for item in build_aurelia_2024_combat_profiles() if item.level == 19)
        assert fingerprint.max_hp == 156
        assert ("lay-on-hands", 95) in fingerprint.resources
        assert ("spell-slot-5", 2) in fingerprint.resources
        assert ("boon-combat-prowess", 1) in fingerprint.resources

        assert_character_build_raw_ready(profile, hero)
        assert_pregen_combat_stats(hero, fingerprint)
        assert_character_resources_raw_ready(hero, profile, fingerprint)
    except Exception:
        logger.exception("Paladin 19 Epic Boon certification failed.")
        raise

# Exact-head refresh after generated artifact commit.

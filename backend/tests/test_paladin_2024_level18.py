from __future__ import annotations

import logging

from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats

logger = logging.getLogger(__name__)


def test_level_eighteen_expands_existing_paladin_auras_to_thirty_feet() -> None:
    try:
        hero = build_aurelia_brightshield_2024(18)
        previous = build_aurelia_brightshield_2024(17)
        profile = build_aurelia_brightshield_2024_profile(18)

        assert hero.name == previous.name
        assert hero.level == 18
        assert profile.final_ability_scores is not None
        assert profile.final_ability_scores == build_aurelia_brightshield_2024_profile(17).final_ability_scores
        assert hero.max_hp == 148
        assert hero.weapon_attack.attack_bonus == 11
        assert hero.skill_bonuses["persuasion"] == 10

        protection = hero.progression_features.friendly_saving_throw_aura
        assert protection is not None
        assert protection.radius_ft == 30
        assert protection.flat_bonus == 4

        condition_auras = {
            item.source_id: item
            for item in hero.progression_features.friendly_condition_immunity_auras
        }
        assert condition_auras["aura-of-devotion-2024"].radius_ft == 30
        assert condition_auras["aura-of-devotion-2024"].condition_id == "charmed"
        assert condition_auras["aura-of-courage-2024"].radius_ft == 30
        assert condition_auras["aura-of-courage-2024"].condition_id == "frightened"

        smite_cover = next(
            item for item in hero.timed_self_buff_actions
            if item.id == "smite-of-protection-2024"
        )
        assert smite_cover.friendly_cover_aura is not None
        assert smite_cover.friendly_cover_aura.radius_ft == 30
        assert smite_cover.friendly_cover_aura.cover_bonus == 2

        resources = {item.id: item.max_uses for item in hero.resources}
        assert resources == {
            "lay-on-hands": 90,
            "spell-slot-1": 4,
            "paladins-smite-free-cast": 1,
            "channel-divinity": 3,
            "spell-slot-2": 3,
            "faithful-steed-free-cast": 1,
            "spell-slot-3": 3,
            "spell-slot-4": 3,
            "spell-slot-5": 1,
        }

        audits = {item.feature_id: item for item in profile.feature_audits}
        aura_expansion = audits["aura-expansion"]
        assert aura_expansion.combat_relevant is True
        assert aura_expansion.automated is True

        fingerprint = next(
            item for item in build_aurelia_2024_combat_profiles()
            if item.level == 18
        )
        assert fingerprint.max_hp == 148
        assert ("lay-on-hands", 90) in fingerprint.resources
        assert ("spell-slot-5", 1) in fingerprint.resources

        assert_character_build_raw_ready(profile, hero)
        assert_pregen_combat_stats(hero, fingerprint)
        assert_character_resources_raw_ready(hero, profile, fingerprint)
    except Exception:
        logger.exception("Paladin 18 Aura Expansion certification failed.")
        raise

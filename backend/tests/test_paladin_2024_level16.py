from __future__ import annotations

import logging

from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats

logger = logging.getLogger(__name__)


def test_level_sixteen_advances_same_aurelia_with_charisma_asi() -> None:
    try:
        hero = build_aurelia_brightshield_2024(16)
        previous = build_aurelia_brightshield_2024(15)
        profile = build_aurelia_brightshield_2024_profile(16)
        previous_profile = build_aurelia_brightshield_2024_profile(15)

        assert hero.name == previous.name
        assert hero.level == 16
        assert previous_profile.final_ability_scores is not None
        assert profile.final_ability_scores is not None
        assert previous_profile.final_ability_scores.charisma == 17
        assert profile.final_ability_scores.charisma == 19
        assert profile.final_ability_scores.strength == 20
        assert hero.max_hp == 132
        assert hero.armor_class == 19
        assert hero.weapon_attack.attack_bonus == 10
        assert hero.weapon_attack.damage_bonus == 5
        assert hero.skill_bonuses["persuasion"] == 9
        assert hero.skill_bonuses["intimidation"] == 9

        aura = hero.progression_features.friendly_saving_throw_aura
        assert aura is not None
        assert aura.radius_ft == 10
        assert aura.flat_bonus == 4

        abjure = hero.saving_throw_actions[0]
        assert abjure.save_dc == 17

        assert {item.id: item.max_uses for item in hero.resources} == {
            "lay-on-hands": 80,
            "spell-slot-1": 4,
            "paladins-smite-free-cast": 1,
            "channel-divinity": 3,
            "spell-slot-2": 3,
            "faithful-steed-free-cast": 1,
            "spell-slot-3": 3,
            "spell-slot-4": 2,
        }

        package = canonical_spell_package("paladin", 16, "2024", 4)
        previous_package = canonical_spell_package("paladin", 15, "2024", 3)
        assert package is not None and previous_package is not None
        assert len(package.spells) == 12
        assert package.spells == previous_package.spells

        audits = {item.feature_id: item for item in profile.feature_audits}
        asi = audits["ability-score-improvement-l16"]
        assert asi.combat_relevant is True
        assert asi.automated is True

        fingerprint = next(item for item in build_aurelia_2024_combat_profiles() if item.level == 16)
        assert fingerprint.abilities.charisma == 19
        assert fingerprint.max_hp == 132
        assert ("lay-on-hands", 80) in fingerprint.resources

        assert_character_build_raw_ready(profile, hero)
        assert_pregen_combat_stats(hero, fingerprint)
        assert_character_resources_raw_ready(hero, profile, fingerprint)
    except Exception:
        logger.exception("Paladin 16 cumulative ASI certification failed.")
        raise

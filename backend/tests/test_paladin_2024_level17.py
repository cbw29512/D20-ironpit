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


def test_level_seventeen_advances_persistent_aurelia_and_binds_2024_flame_strike() -> None:
    try:
        hero = build_aurelia_brightshield_2024(17)
        previous = build_aurelia_brightshield_2024(16)
        profile = build_aurelia_brightshield_2024_profile(17)

        assert hero.name == previous.name
        assert hero.level == 17
        assert profile.final_ability_scores is not None
        assert profile.final_ability_scores.strength == 20
        assert profile.final_ability_scores.charisma == 19
        assert hero.max_hp == 140
        assert hero.weapon_attack.attack_bonus == 11
        assert hero.weapon_attack.damage_bonus == 5
        assert hero.skill_bonuses["athletics"] == 11
        assert hero.skill_bonuses["persuasion"] == 10

        aura = hero.progression_features.friendly_saving_throw_aura
        assert aura is not None
        assert aura.flat_bonus == 4

        abjure = hero.saving_throw_actions[0]
        assert abjure.dc == 18
        assert abjure.max_targets == 4

        flame_strike = next(item for item in hero.spell_save_actions if item.id == "flame-strike")
        wave = next(item for item in hero.spell_save_actions if item.id == "destructive-wave")
        assert flame_strike.id == "flame-strike"
        assert flame_strike.level == 5
        assert flame_strike.range_ft == 60
        assert flame_strike.dc == 18
        assert flame_strike.save_ability == "dexterity"
        assert flame_strike.success_damage == "half"
        assert [(part.dice_count, part.dice_size, part.damage_type) for part in flame_strike.damage_components] == [
            (5, 6, "fire"),
            (5, 6, "radiant"),
        ]
        assert wave.dc == 18
        assert wave.save_ability == "constitution"
        assert wave.area is not None
        assert (wave.area.shape, wave.area.origin, wave.area.radius_ft) == ("emanation", "self", 30)
        assert [(part.dice_count, part.dice_size, part.damage_type) for part in wave.damage_components] == [
            (5, 6, "thunder"),
            (5, 6, "radiant"),
        ]

        resources = {item.id: item.max_uses for item in hero.resources}
        assert resources == {
            "lay-on-hands": 85,
            "spell-slot-1": 4,
            "paladins-smite-free-cast": 1,
            "channel-divinity": 3,
            "spell-slot-2": 3,
            "faithful-steed-free-cast": 1,
            "spell-slot-3": 3,
            "spell-slot-4": 3,
            "spell-slot-5": 1,
        }

        package = canonical_spell_package("paladin", 17, "2024", 4)
        assert package is not None
        assert len(package.spells) == 14
        assert [spell.id for spell in package.spells[-2:]] == [
            "destructive-wave",
            "greater-restoration",
        ]
        assert {"commune", "flame-strike"}.issubset({
            spell.id for spell in package.always_prepared_spells
        })

        audits = {item.feature_id: item for item in profile.feature_audits}
        assert audits["oath-spells-level17"].automated is True

        fingerprint = next(item for item in build_aurelia_2024_combat_profiles() if item.level == 17)
        assert fingerprint.max_hp == 140
        assert ("spell-slot-4", 3) in fingerprint.resources
        assert ("spell-slot-5", 1) in fingerprint.resources

        assert_character_build_raw_ready(profile, hero)
        assert_pregen_combat_stats(hero, fingerprint)
        assert_character_resources_raw_ready(hero, profile, fingerprint)
    except Exception:
        logger.exception("Paladin 17 certification failed.")
        raise

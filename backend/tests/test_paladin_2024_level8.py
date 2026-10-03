from __future__ import annotations

from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_2024_paladin_level_eight_asi_is_raw_ready() -> None:
    profile = build_aurelia_brightshield_2024_profile(8)
    hero = build_aurelia_brightshield_2024(8)
    combat = next(
        item for item in build_aurelia_2024_combat_profiles() if item.level == 8
    )

    assert profile.final_ability_scores.strength == 20
    assert profile.final_ability_scores.charisma == 15
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [
        ("strength", 2),
        ("strength", 1),
        ("charisma", 1),
    ]

    assert (hero.max_hp, hero.armor_class) == (68, 19)
    assert hero.weapon_attack.attack_bonus == 8
    assert hero.weapon_attack.damage_bonus == 5
    assert hero.skill_bonuses["athletics"] == 8
    assert hero.skill_bonuses["persuasion"] == 5

    aura = hero.progression_features.friendly_saving_throw_aura
    assert aura is not None
    assert aura.flat_bonus == 2
    assert aura.radius_ft == 10

    assert {item.id: item.max_uses for item in hero.resources} == {
        "lay-on-hands": 40,
        "spell-slot-1": 4,
        "paladins-smite-free-cast": 1,
        "channel-divinity": 2,
        "spell-slot-2": 3,
        "faithful-steed-free-cast": 1,
    }

    package = canonical_spell_package("paladin", 8, "2024", 2)
    assert package is not None
    assert [spell.id for spell in package.spells] == [
        "cure-wounds",
        "divine-favor",
        "bless",
        "searing-smite",
        "thunderous-smite",
        "shining-smite",
        "lesser-restoration",
    ]

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["ability-score-improvement-l8"].automated is True

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)


def test_2024_paladin_level_seven_snapshot_remains_stable_after_level_eight() -> None:
    level7 = build_aurelia_brightshield_2024(7)
    assert level7.ability_scores.strength == 19
    assert level7.ability_scores.charisma == 14
    assert level7.weapon_attack.attack_bonus == 7
    assert level7.weapon_attack.damage_bonus == 4

from __future__ import annotations

from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_2024_paladin_level_four_asi_and_spell_progression_are_raw_ready() -> None:
    profile = build_aurelia_brightshield_2024_profile(4)
    hero = build_aurelia_brightshield_2024(4)
    combat = build_aurelia_2024_combat_profiles()[-1]

    assert profile.final_ability_scores.strength == 19
    assert profile.final_ability_scores.charisma == 14
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [
        ("strength", 2),
    ]
    assert (hero.max_hp, hero.armor_class) == (36, 19)
    assert hero.weapon_attack.attack_bonus == 6
    assert hero.weapon_attack.damage_bonus == 4
    assert hero.skill_bonuses["athletics"] == 6
    assert {item.id: item.max_uses for item in hero.resources} == {
        "lay-on-hands": 20,
        "spell-slot-1": 3,
        "paladins-smite-free-cast": 1,
        "channel-divinity": 2,
    }

    package = canonical_spell_package("paladin", 4, "2024", 2)
    assert package is not None
    assert [spell.id for spell in package.spells] == [
        "cure-wounds",
        "divine-favor",
        "bless",
        "searing-smite",
        "thunderous-smite",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "divine-smite",
        "protection-from-evil-and-good",
        "shield-of-faith",
    ]
    assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["ability-score-improvement-l4"].automated is True

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)

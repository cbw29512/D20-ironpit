from __future__ import annotations

from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_2024_paladin_level_five_progression_is_raw_ready() -> None:
    profile = build_aurelia_brightshield_2024_profile(5)
    hero = build_aurelia_brightshield_2024(5)
    combat = next(
        item for item in build_aurelia_2024_combat_profiles() if item.level == 5
    )

    assert profile.final_ability_scores.strength == 19
    assert (hero.max_hp, hero.armor_class) == (44, 19)
    assert hero.weapon_attack.attack_bonus == 7
    assert hero.weapon_attack.damage_bonus == 4
    assert hero.skill_bonuses["athletics"] == 7

    assert hero.attack_action is not None
    assert hero.attack_action.id == "extra-attack"
    assert len(hero.attack_action.slots) == 2
    assert all(
        set(slot.attack_ids) == {"aurelia-longsword", "aurelia-javelin"}
        for slot in hero.attack_action.slots
    )

    assert {item.id: item.max_uses for item in hero.resources} == {
        "lay-on-hands": 25,
        "spell-slot-1": 4,
        "paladins-smite-free-cast": 1,
        "channel-divinity": 2,
        "spell-slot-2": 2,
        "faithful-steed-free-cast": 1,
    }

    package = canonical_spell_package("paladin", 5, "2024", 2)
    assert package is not None
    assert [spell.id for spell in package.spells] == [
        "cure-wounds",
        "divine-favor",
        "bless",
        "searing-smite",
        "thunderous-smite",
        "shining-smite",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "divine-smite",
        "protection-from-evil-and-good",
        "shield-of-faith",
        "find-steed",
        "aid",
        "zone-of-truth",
    ]
    assert package.spells[-1].required_capabilities == ["arena-out-of-scope"]
    find_steed = next(spell for spell in package.always_prepared_spells if spell.id == "find-steed")
    assert find_steed.required_capabilities == ["arena-unavailable-summon"]

    aid = next(spell for spell in hero.defensive_spell_actions if spell.id == "aid")
    assert (
        aid.level,
        aid.action_cost,
        aid.range_ft,
        aid.duration_minutes,
        aid.target_count,
        aid.max_hp_increase,
        aid.current_hp_increase,
    ) == (2, "action", 30, 480, 3, 5, 5)

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["extra-attack"].automated is True
    assert audits["faithful-steed"].automated is False
    assert "no-summons" in (audits["faithful-steed"].notes or "").casefold()

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)

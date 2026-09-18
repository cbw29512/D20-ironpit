from __future__ import annotations

from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.paladin_2014_spell_package import prepared_count_2014
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile


def test_level_one_2014_paladin_has_no_spellcasting_package() -> None:
    assert canonical_spell_package("paladin", 1, "2014", 2) is None
    assert prepared_count_2014(1, 2) == 0


def test_aurelia_prepared_spell_counts_follow_2014_formula() -> None:
    expected = {
        2: 3, 3: 3, 4: 4, 5: 4, 6: 5,
        7: 5, 8: 7, 9: 7, 10: 8,
    }
    for level, count in expected.items():
        profile = build_aurelia_brightshield_2014_profile(level)
        charisma = profile.final_ability_scores.modifier("charisma")
        package = canonical_spell_package("paladin", level, "2014", charisma)
        assert package is not None
        assert len(package.spells) == count
        assert prepared_count_2014(level, charisma) == count


def test_devotion_oath_spells_unlock_without_using_prepared_count() -> None:
    level3 = canonical_spell_package("paladin", 3, "2014", 2)
    level5 = canonical_spell_package("paladin", 5, "2014", 2)
    level9 = canonical_spell_package("paladin", 9, "2014", 3)
    assert level3 is not None and level5 is not None and level9 is not None
    assert [spell.id for spell in level3.always_prepared_spells] == [
        "protection-from-evil-and-good", "sanctuary",
    ]
    assert [spell.id for spell in level5.always_prepared_spells] == [
        "protection-from-evil-and-good", "sanctuary", "lesser-restoration", "zone-of-truth",
    ]
    assert [spell.id for spell in level9.always_prepared_spells] == [
        "protection-from-evil-and-good", "sanctuary", "lesser-restoration", "zone-of-truth",
        "beacon-of-hope", "dispel-magic",
    ]


def test_all_aurelia_profiles_pass_ruleset_aware_canonical_policy() -> None:
    for level in range(1, 11):
        assert_canonical_profile_policy(build_aurelia_brightshield_2014_profile(level))

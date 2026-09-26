from __future__ import annotations

from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014


def test_level_two_persists_nyra_and_adds_font_of_magic_resources() -> None:
    hero = build_nyra_emberveil_2014(2)
    profile = build_nyra_emberveil_2014_profile(2)

    assert hero.level == 2
    assert profile.level == 2
    assert profile.character_name == "Nyra Emberveil"
    assert hero.max_hp == 12
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 3,
        "sorcery-points": 2,
    }


def test_level_two_font_of_magic_is_data_bound_to_universal_conversions() -> None:
    hero = build_nyra_emberveil_2014(2)
    actions = {item.id: item for item in hero.resource_conversion_actions}

    assert set(actions) == {"create-spell-slot-1", "convert-spell-slot-1"}
    assert actions["create-spell-slot-1"].source_cost == 2
    assert actions["create-spell-slot-1"].target_resource_id == "spell-slot-1"
    assert actions["create-spell-slot-1"].target_allows_overflow is True
    assert actions["create-spell-slot-1"].automation == "when-all-spell-slots-empty"
    assert actions["convert-spell-slot-1"].source_resource_id == "spell-slot-1"
    assert actions["convert-spell-slot-1"].target_resource_id == "sorcery-points"
    assert actions["convert-spell-slot-1"].target_allows_overflow is False


def test_level_two_spell_package_has_three_legal_known_spells() -> None:
    package = build_sorcerer_2014_spell_package(2)

    assert len(package.cantrips) == 4
    assert [item.id for item in package.spells] == [
        "burning-hands",
        "detect-magic",
        "comprehend-languages",
    ]


def test_level_two_font_of_magic_audit_is_certified() -> None:
    profile = build_nyra_emberveil_2014_profile(2)
    audit = next(item for item in profile.feature_audits if item.feature_id == "font-of-magic")

    assert audit.combat_relevant is True
    assert audit.automated is True

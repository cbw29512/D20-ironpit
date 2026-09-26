from __future__ import annotations

from app.content.ranger_2014_spell_package import build_ranger_2014_spell_package
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_level_seventeen_unlocks_fifth_level_spellcasting() -> None:
    hero = build_rowan_ashtrail_2014(17)
    profile = build_rowan_ashtrail_2014_profile(17)
    package = build_ranger_2014_spell_package(17)

    assert hero.level == 17
    assert profile.level == 17
    assert hero.max_hp == 140
    assert hero.weapon_attack.attack_bonus == 13
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 1,
    }
    assert len(package.spells) == 10
    assert package.spells[-1].id == "commune-with-nature"


def test_level_seventeen_audits_fifth_level_spellcasting_without_fake_combat_runtime() -> None:
    profile = build_rowan_ashtrail_2014_profile(17)
    audit = next(
        item for item in profile.feature_audits
        if item.feature_id == "spellcasting-5th-level"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True
    assert "Commune with Nature" in (audit.notes or "")

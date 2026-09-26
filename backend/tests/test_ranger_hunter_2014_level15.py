from __future__ import annotations

from app.content.ranger_2014_spell_package import build_ranger_2014_spell_package
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_level_fifteen_resources_spell_count_and_evasion() -> None:
    hero = build_rowan_ashtrail_2014(15)
    profile = build_rowan_ashtrail_2014_profile(15)
    package = build_ranger_2014_spell_package(15)

    assert hero.level == 15
    assert profile.level == 15
    assert hero.max_hp == 124
    assert hero.weapon_attack.attack_bonus == 12
    assert hero.progression_features.evasion is True
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 2,
    }
    assert len(package.spells) == 9
    assert package.spells[-1].id == "locate-creature"


def test_level_fifteen_audit_records_universal_evasion_choice() -> None:
    profile = build_rowan_ashtrail_2014_profile(15)
    audit = next(
        item for item in profile.feature_audits
        if item.feature_id == "superior-hunters-defense-evasion"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True
    assert "universal Evasion" in (audit.notes or "")

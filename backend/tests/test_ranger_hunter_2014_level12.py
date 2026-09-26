from __future__ import annotations

from app.content.ranger_2014_spell_package import build_ranger_2014_spell_package
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_level_twelve_asi_and_resources() -> None:
    hero = build_rowan_ashtrail_2014(12)
    profile = build_rowan_ashtrail_2014_profile(12)

    assert hero.level == 12
    assert hero.ability_scores.dexterity == 20
    assert hero.ability_scores.wisdom == 17
    assert hero.max_hp == 100
    assert hero.weapon_attack.attack_bonus == 12
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
    }

    audit = next(
        item for item in profile.feature_audits
        if item.feature_id == "ability-score-improvement-12"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True


def test_level_twelve_known_spells_do_not_fake_a_new_combat_mechanic() -> None:
    package = build_ranger_2014_spell_package(12)
    assert len(package.spells) == 7

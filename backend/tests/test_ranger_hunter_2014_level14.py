from __future__ import annotations

from app.content.ranger_2014_spell_package import build_ranger_2014_spell_package
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_level_fourteen_keeps_level_thirteen_combat_resources() -> None:
    hero = build_rowan_ashtrail_2014(14)
    profile = build_rowan_ashtrail_2014_profile(14)
    package = build_ranger_2014_spell_package(14)

    assert hero.level == 14
    assert profile.level == 14
    assert hero.max_hp == 116
    assert hero.weapon_attack.attack_bonus == 12
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
    }
    assert len(package.spells) == 8


def test_level_fourteen_vanish_is_explicitly_arena_neutral() -> None:
    profile = build_rowan_ashtrail_2014_profile(14)
    audit = next(item for item in profile.feature_audits if item.feature_id == "vanish")

    assert audit.combat_relevant is False
    assert audit.automated is False
    assert "no automatic legal Hide position" in (audit.notes or "")

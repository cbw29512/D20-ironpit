from __future__ import annotations

from app.content.character_resource_audit import audit_character_resources
from app.content.ranger_hunter_2014_combat_profile import build_rowan_2014_combat_profile
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_ranger_level_one_resources_are_independently_certified_as_empty() -> None:
    template = build_rowan_ashtrail_2014(1)
    profile = build_rowan_ashtrail_2014_profile(1)
    combat_profile = build_rowan_2014_combat_profile(1)

    assert template.resources == []
    assert combat_profile.resources == ()
    assert audit_character_resources(template, profile, combat_profile) == []


def test_ranger_level_eleven_spell_slots_match_independent_resource_audit() -> None:
    template = build_rowan_ashtrail_2014(11)
    profile = build_rowan_ashtrail_2014_profile(11)
    combat_profile = build_rowan_2014_combat_profile(11)

    assert {item.id: item.max_uses for item in template.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
    }
    assert dict(combat_profile.resources) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
    }
    assert audit_character_resources(template, profile, combat_profile) == []

from __future__ import annotations

from app.content.ranger_2014_spell_package import build_ranger_2014_spell_package
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_level_thirteen_unlocks_fourth_level_spellcasting() -> None:
    hero = build_rowan_ashtrail_2014(13)
    profile = build_rowan_ashtrail_2014_profile(13)
    package = build_ranger_2014_spell_package(13)

    assert hero.level == 13
    assert profile.level == 13
    assert hero.max_hp == 108
    assert hero.weapon_attack.attack_bonus == 12
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
    }
    assert len(package.spells) == 8
    assert package.spells[-1].id == "freedom-of-movement"


def test_level_thirteen_reuses_shared_freedom_of_movement() -> None:
    hero = build_rowan_ashtrail_2014(13)
    spell = next(
        action for action in hero.defensive_spell_actions
        if action.id == "freedom-of-movement"
    )

    assert spell.level == 4
    assert spell.action_cost == "action"
    assert spell.concentration is False
    counters = [effect.debuff_counter for effect in spell.modifier_effects]
    assert any(counter and counter.debuff_id == "difficult-terrain" for counter in counters)
    assert any(counter and counter.debuff_id == "grappled" for counter in counters)

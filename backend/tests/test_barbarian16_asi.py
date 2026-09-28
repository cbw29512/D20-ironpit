from __future__ import annotations

from app.content.barbarian_level16_profile import build_rokhan_stonefury_level16_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry


def _resource_maxima(template) -> dict[str, int]:
    try:
        return {item.id: item.max_uses for item in template.resources}
    except Exception as exc:
        raise AssertionError("Unable to inspect Barbarian resources.") from exc


def test_level16_asi_and_rage_damage_are_parameter_deltas() -> None:
    profile = build_rokhan_stonefury_level16_profile()
    level15 = build_rokhan_stonefury_level(15)
    level16 = build_rokhan_stonefury_level(16)

    assert profile.level == 16
    assert profile.subclass_id == "path-berserker"
    assert profile.final_ability_scores.constitution == 20
    assert profile.final_ability_scores.strength == 20

    assert level15.ability_scores is not None
    assert level16.ability_scores is not None
    assert level15.ability_scores.constitution == 18
    assert level16.ability_scores.constitution == 20
    assert level15.armor_class == 15
    assert level16.armor_class == 16
    assert level15.max_hp == 170
    assert level16.max_hp == 197
    assert level15.rage_damage_bonus == 3
    assert level16.rage_damage_bonus == 4

    assert level16.progression_features.rage_persists_without_maintenance is True
    assert level16.initiative_resource_refill_grants == level15.initiative_resource_refill_grants
    assert _resource_maxima(level16) == _resource_maxima(level15)
    assert ("barbarian", 16, "canonical") in build_certified_hero_registry()


def test_level16_preserves_existing_berserker_combat_actions() -> None:
    level15 = build_rokhan_stonefury_level(15)
    level16 = build_rokhan_stonefury_level(16)

    assert [item.id for item in level16.saving_throw_actions] == [
        item.id for item in level15.saving_throw_actions
    ]
    assert [item.id for item in level16.resource_conversion_actions] == [
        item.id for item in level15.resource_conversion_actions
    ]
    assert level16.progression_features.brutal_strike_damage_dice == 1
    assert level16.progression_features.brutal_strike_max_effects == 1

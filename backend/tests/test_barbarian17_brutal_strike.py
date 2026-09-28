from __future__ import annotations

from app.content.barbarian_level17_profile import build_rokhan_stonefury_level17_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry


def _resource_maxima(template) -> dict[str, int]:
    try:
        return {item.id: item.max_uses for item in template.resources}
    except Exception as exc:
        raise AssertionError("Unable to inspect Barbarian resources.") from exc


def test_level17_improved_brutal_strike_is_existing_capability_scaling() -> None:
    profile = build_rokhan_stonefury_level17_profile()
    level16 = build_rokhan_stonefury_level(16)
    level17 = build_rokhan_stonefury_level(17)

    assert profile.level == 17
    assert profile.subclass_id == "path-berserker"
    assert level17.max_hp == 209
    assert level17.rage_damage_bonus == 4
    assert level17.progression_features.brutal_strike_damage_dice == 2
    assert level17.progression_features.brutal_strike_max_effects == 2
    assert set(level17.progression_features.brutal_strike_effect_ids) == {
        "forceful-blow",
        "hamstring-blow",
        "staggering-blow",
        "sundering-blow",
    }

    assert _resource_maxima(level16)["rage"] == 5
    assert _resource_maxima(level17)["rage"] == 6
    assert (("barbarian", 17, "canonical") in build_certified_hero_registry())


def test_level17_preserves_level16_berserker_actions_and_persistent_rage() -> None:
    level16 = build_rokhan_stonefury_level(16)
    level17 = build_rokhan_stonefury_level(17)

    assert [item.id for item in level17.saving_throw_actions] == [
        item.id for item in level16.saving_throw_actions
    ]
    assert [item.id for item in level17.resource_conversion_actions] == [
        item.id for item in level16.resource_conversion_actions
    ]
    assert level17.progression_features.rage_persists_without_maintenance is True
    assert len(level17.initiative_resource_refill_grants) == 1
    assert level17.initiative_resource_refill_grants[0].resource_id == "rage"
    assert level17.initiative_resource_refill_grants[0].when_at_or_below == 5
    assert level17.initiative_resource_refill_grants[0].restore_to_max is True

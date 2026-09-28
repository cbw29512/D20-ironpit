from __future__ import annotations

from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_level15 import build_seraphine_dawnshield_level15_profile
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def _resources(template) -> dict[str, int]:
    try:
        return {item.id: item.max_uses for item in template.resources}
    except Exception as exc:
        raise AssertionError("Unable to inspect Cleric resources.") from exc


def test_level_fifteen_sunburst_reuses_universal_save_condition_runtime() -> None:
    hero = build_seraphine_dawnshield_level(15)
    profile = build_seraphine_dawnshield_level15_profile()
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("cleric", 15)

    assert hero.max_hp == 78
    assert (hero.ability_scores.wisdom, hero.ability_scores.charisma) == (20, 17)
    assert _resources(hero)["spell-slot-8"] == 1
    assert _resources(hero)["adrenaline-rush"] == 5

    sunburst = next(item for item in hero.spell_save_actions if item.id == "sunburst")
    assert sunburst.level == 8
    assert sunburst.range_ft == 150
    assert sunburst.area is not None
    assert (sunburst.area.shape, sunburst.area.origin, sunburst.area.radius_ft) == (
        "radius", "point", 60,
    )
    assert (sunburst.save_ability, sunburst.dc) == ("constitution", 18)
    assert (sunburst.damage_dice_count, sunburst.damage_dice_size) == (12, 6)
    assert sunburst.damage_type == "radiant"
    assert sunburst.success_damage == "half"
    assert sunburst.effect_tags == ["blinded"]

    rider = sunburst.failed_save_timed_effect
    assert rider is not None
    assert rider.effect_id == "blinded"
    assert rider.duration_rounds == 10
    assert rider.expiry_timing == "source_turn_start"
    assert rider.repeat_save_ability == "constitution"
    assert rider.repeat_save_dc == 18
    assert rider.repeat_save_timing == "target_turn_end"

    assert len(package.spells) == 18
    assert package.spells[-1].id == "sunburst"

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_certified_registry_exposes_cleric_level_fifteen() -> None:
    registry = build_certified_hero_registry()
    assert registry[("cleric", 15, "canonical")][1] == "seraphine-dawnshield-l15"

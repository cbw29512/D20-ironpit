from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_high_profile import build_seraphine_dawnshield_level9_profile
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def _resources(template) -> dict[str, int]:
    return {item.id: item.max_uses for item in template.resources}


def test_level_nine_uses_simple_upcast_damage_and_mass_healing() -> None:
    level8 = build_seraphine_dawnshield_level(8)
    hero = build_seraphine_dawnshield_level(9)
    profile = build_seraphine_dawnshield_level9_profile()
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("cleric", 9)

    assert hero.max_hp == level8.max_hp + 5 == 48
    assert (hero.ability_scores.wisdom, hero.ability_scores.charisma) == (20, 15)
    assert _resources(hero) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 1,
        "channel-divinity": 3,
        "adrenaline-rush": 4,
        "relentless-endurance": 1,
    }

    upcast = next(item for item in hero.spell_save_actions if item.id == "inflict-wounds-l5")
    assert (upcast.level, upcast.damage_dice_count, upcast.damage_dice_size) == (5, 6, 10)
    assert upcast.damage_type == "necrotic"
    assert upcast.success_damage == "half"
    assert upcast.dc == 17

    mass = next(item for item in hero.healing_actions if item.id == "mass-cure-wounds")
    assert (mass.max_targets, mass.dice_count, mass.dice_size) == (6, 5, 8)
    assert mass.healing_bonus == 12
    assert mass.resource_id == "spell-slot-5"
    assert mass.action_cost == "action"

    assert len(package.spells) == 14
    assert [spell.id for spell in package.spells][-2:] == ["flame-strike", "insect-plague"]
    assert [spell.id for spell in package.always_prepared_spells][-2:] == [
        "greater-restoration", "mass-cure-wounds",
    ]

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["cleric-combat-spells-5"].automated is True
    assert audits["mass-cure-wounds"].automated is True
    assert audits["inflict-wounds-upcast-l5"].automated is True
    assert audits["greater-restoration"].combat_relevant is False

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_certified_registry_exposes_cleric_level_nine_only() -> None:
    registry = build_certified_hero_registry()
    assert registry[("cleric", 9, "canonical")] == (
        "Seraphine Dawnshield", "seraphine-dawnshield-l9",
    )
    assert ("cleric", 10, "canonical") not in registry

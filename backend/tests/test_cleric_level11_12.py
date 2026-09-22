from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_high_profile import (
    build_seraphine_dawnshield_level11_profile,
    build_seraphine_dawnshield_level12_profile,
)
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def _resources(template) -> dict[str, int]:
    return {item.id: item.max_uses for item in template.resources}


def test_level_eleven_uses_simple_sixth_level_upcasts() -> None:
    level10 = build_seraphine_dawnshield_level(10)
    hero = build_seraphine_dawnshield_level(11)
    profile = build_seraphine_dawnshield_level11_profile()
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("cleric", 11)

    assert hero.max_hp == level10.max_hp + 5 == 58
    assert _resources(hero) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "channel-divinity": 3,
        "divine-intervention": 1,
        "adrenaline-rush": 4,
        "relentless-endurance": 1,
    }

    damage = next(item for item in hero.spell_save_actions if item.id == "inflict-wounds-l6")
    healing = next(item for item in hero.healing_actions if item.id == "mass-cure-wounds-l6")
    assert (damage.level, damage.damage_dice_count, damage.damage_dice_size) == (6, 7, 10)
    assert damage.damage_type == "necrotic"
    assert damage.success_damage == "half"
    assert damage.dc == 17

    assert (healing.dice_count, healing.dice_size, healing.healing_bonus) == (6, 8, 13)
    assert healing.resource_id == "spell-slot-6"
    assert healing.max_targets == 6

    assert len(package.spells) == 16
    assert package.spells[-1].id == "heal"

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["cleric-combat-spells-6"].automated is True
    assert audits["inflict-wounds-upcast-l6"].automated is True
    assert audits["mass-cure-wounds-upcast-l6"].automated is True
    assert audits["heal"].combat_relevant is False

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_twelve_is_incremental_and_updates_charisma_only() -> None:
    level11 = build_seraphine_dawnshield_level(11)
    hero = build_seraphine_dawnshield_level(12)
    profile = build_seraphine_dawnshield_level12_profile()
    combat = build_pregen_combat_profiles()[hero.id]

    assert hero.max_hp == level11.max_hp + 5 == 63
    assert (hero.ability_scores.wisdom, hero.ability_scores.charisma) == (20, 17)
    assert hero.spell_save_actions[-1].id == "inflict-wounds-l6"
    assert hero.healing_actions[-1].id == "mass-cure-wounds-l6"
    assert hero.saving_throw_bonuses["charisma"] == 7
    assert hero.skill_bonuses["persuasion"] == 7

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["ability-score-improvement-l12"].automated is True

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_certified_registry_exposes_cleric_levels_eleven_and_twelve() -> None:
    registry = build_certified_hero_registry()
    assert registry[("cleric", 11, "canonical")] == (
        "Seraphine Dawnshield", "seraphine-dawnshield-l11",
    )
    assert registry[("cleric", 12, "canonical")] == (
        "Seraphine Dawnshield", "seraphine-dawnshield-l12",
    )
    assert ("cleric", 13, "canonical") not in registry

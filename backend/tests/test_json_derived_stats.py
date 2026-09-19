from pathlib import Path

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.json_combatant_compiler import (
    compile_hero_definition,
    fold_hero_level,
    load_hero_bundle,
    load_hero_catalog,
)
from app.content.json_hero_derived import derive_armor_class, derive_hit_points


ROOT = Path(__file__).resolve().parents[2]


def _catalog_cases():
    cases = []
    for edition in ("2014", "2024"):
        catalog = load_hero_catalog(ROOT / f"data/heroes/{edition}/heroes.json")
        for identity in catalog.heroes:
            cases.append((edition, identity.id, identity.level_range[0], identity.level_range[1]))
    return cases


@pytest.mark.parametrize("edition,slug,low,high", _catalog_cases())
def test_certified_track_hit_points_match_raw_recast_math(edition, slug, low, high):
    identity, progression, subclass, species, track, _build = load_hero_bundle(ROOT, edition, slug)
    for level in range(low, high + 1):
        folded = fold_hero_level(progression, subclass, species, track, level)
        derived = derive_hit_points(
            level, progression.hit_die, int(folded["ability_scores"]["constitution"]),
        )
        assert derived == folded["max_hp"]
        if level <= len(track.hp_by_level):
            assert derived == track.hp_by_level[level - 1]


@pytest.mark.parametrize("edition,slug,low,high", _catalog_cases())
def test_certified_track_armor_class_matches_worn_or_unarmored_formula(edition, slug, low, high):
    identity, progression, subclass, species, track, build = load_hero_bundle(ROOT, edition, slug)
    for level in range(low, high + 1):
        folded = fold_hero_level(progression, subclass, species, track, level)
        definition = compile_hero_definition(identity.id, identity.name, folded, build)
        if definition.unsupported_capabilities:
            continue
        compiled = compile_combatant(definition)
        fighting_styles = list(folded.get("fighting_styles") or [])
        if not fighting_styles and build.fighting_style:
            fighting_styles = [build.fighting_style]
        derived = derive_armor_class(
            str(build.visual.get("armor") or ""),
            dict(folded["ability_scores"]),
            fighting_styles,
            wielding_shield=build.visual.get("off_hand") == "shield",
            unarmored_defense_abilities=list(progression.unarmored_defense_abilities),
            unarmored_defense_allows_shield=progression.unarmored_defense_allows_shield,
        )
        assert compiled.armor_class == derived
        if level <= len(track.ac_by_level):
            assert derived == track.ac_by_level[level - 1]


def test_karnok_level_4_constitution_asi_recasts_hit_points_from_level_one():
    _identity, progression, subclass, species, track, _build = load_hero_bundle(
        ROOT, "2024", "karnok-stoneward",
    )
    level3 = fold_hero_level(progression, subclass, species, track, 3)
    level4 = fold_hero_level(progression, subclass, species, track, 4)
    assert level3["max_hp"] == 28
    assert level4["ability_scores"]["constitution"] == 16
    assert level4["max_hp"] == 40
    assert derive_hit_points(4, 10, 16) == 40


def test_karnok_chain_mail_defense_ac_ignores_dexterity():
    identity, progression, subclass, species, track, build = load_hero_bundle(
        ROOT, "2024", "karnok-stoneward",
    )
    folded = fold_hero_level(progression, subclass, species, track, 14)
    compiled = compile_combatant(compile_hero_definition(identity.id, identity.name, folded, build))
    assert folded["ability_scores"]["dexterity"] == 15
    assert compiled.armor_class == 17


def test_fingerprint_mismatch_fails_closed():
    _identity, progression, subclass, species, track, _build = load_hero_bundle(
        ROOT, "2024", "karnok-stoneward",
    )
    broken = track.model_copy(update={"hp_by_level": [12, 99] + track.hp_by_level[2:]})
    with pytest.raises(ValueError, match="max_hp derived"):
        fold_hero_level(progression, subclass, species, track.model_copy(update={
            "hp_by_level": broken.hp_by_level,
        }), 2)


def test_2024_karnok_level_15_compiles_and_high_level_survivor_is_supported():
    identity, progression, subclass, species, track, build = load_hero_bundle(
        ROOT, "2024", "karnok-stoneward",
    )
    folded = fold_hero_level(progression, subclass, species, track, 15)
    definition = compile_hero_definition(identity.id, identity.name, folded, build)
    assert definition.unsupported_capabilities == []
    compiled = compile_combatant(definition)
    assert compiled.max_hp == 169
    assert compiled.armor_class == 17
    assert compiled.progression_features.critical_hit_minimum == 18
    assert compiled.ability_scores.dexterity == 15

    folded = fold_hero_level(progression, subclass, species, track, 16)
    compiled = compile_combatant(compile_hero_definition(identity.id, identity.name, folded, build))
    assert compiled.ability_scores.dexterity == 17

    folded = fold_hero_level(progression, subclass, species, track, 18)
    definition = compile_hero_definition(identity.id, identity.name, folded, build)
    assert definition.unsupported_capabilities == []
    compiled = compile_combatant(definition)
    assert compiled.progression_features.survivor_heal_amount == 10
    assert compiled.progression_features.death_save_advantage is True
    assert compiled.progression_features.death_save_nat20_minimum == 18

    folded = fold_hero_level(progression, subclass, species, track, 19)
    compiled = compile_combatant(compile_hero_definition(identity.id, identity.name, folded, build))
    assert compiled.ability_scores.dexterity == 18
    assert compiled.progression_features.peerless_aim is True

    folded = fold_hero_level(progression, subclass, species, track, 20)
    compiled = compile_combatant(compile_hero_definition(identity.id, identity.name, folded, build))
    assert compiled.attack_action is not None
    assert len(compiled.attack_action.slots) == 4


def test_2014_karnok_archery_adds_plus_two_to_longbow_at_level_10():
    identity, progression, subclass, species, track, build = load_hero_bundle(
        ROOT, "2014", "karnok-stoneward-2014",
    )
    before = compile_combatant(compile_hero_definition(
        identity.id, identity.name,
        fold_hero_level(progression, subclass, species, track, 9),
        build,
    ))
    after = compile_combatant(compile_hero_definition(
        identity.id, identity.name,
        fold_hero_level(progression, subclass, species, track, 10),
        build,
    ))
    bow_before = next(item for item in before.alternate_weapon_attacks if item.weapon.id == "longbow")
    bow_after = next(item for item in after.alternate_weapon_attacks if item.weapon.id == "longbow")
    assert "Archery" not in (before.fighting_styles or [])
    assert "Archery" in (after.fighting_styles or [])
    assert bow_after.attack_bonus == bow_before.attack_bonus + 2


def _compile(edition, slug, level):
    identity, progression, subclass, species, track, build = load_hero_bundle(ROOT, edition, slug)
    folded = fold_hero_level(progression, subclass, species, track, level)
    definition = compile_hero_definition(identity.id, identity.name, folded, build)
    assert definition.unsupported_capabilities == []
    return compile_combatant(definition)


def test_2014_rokhan_json_compiles_retaliation_through_primal_champion():
    hp = [14, 23, 32, 41, 50, 59, 68, 77, 86, 95, 104, 125, 135, 145, 155, 181, 192, 203, 233, 285]
    for level, max_hp in enumerate(hp, start=1):
        hero = _compile("2014", "rokhan-stonefury-2014", level)
        assert (hero.max_hp, hero.speed_ft) == (max_hp, 30 if level < 5 else 40)
    l14 = _compile("2014", "rokhan-stonefury-2014", 14)
    assert l14.damage_reaction_attack is not None
    assert l14.damage_reaction_attack.source_feature == "retaliation"
    assert _compile("2014", "rokhan-stonefury-2014", 15).progression_features.persistent_rage_2014 is True
    assert _compile("2014", "rokhan-stonefury-2014", 17).progression_features.brutal_critical_dice == 3
    l18 = _compile("2014", "rokhan-stonefury-2014", 18)
    assert l18.progression_features.ability_check_minimums[0].source_id == "indomitable-might"
    l20 = _compile("2014", "rokhan-stonefury-2014", 20)
    assert l20.ability_scores.model_dump()["strength"] == 24
    assert l20.ability_scores.model_dump()["constitution"] == 24
    assert l20.unlimited_resource_ids == ["rage"]
    assert l20.resources == []


def test_2024_rokhan_json_compiles_through_retaliation():
    l8 = _compile("2024", "rokhan-stonefury", 8)
    assert l8.ability_scores.strength == 20
    l10 = _compile("2024", "rokhan-stonefury", 10)
    assert l10.damage_reaction_attack is not None
    assert l10.damage_reaction_attack.source_feature == "retaliation"
    l12 = _compile("2024", "rokhan-stonefury", 12)
    assert l12.max_hp == 137
    assert l12.ability_scores.constitution == 18

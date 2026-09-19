from pathlib import Path

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.capability_registry import get_capability_definition
from app.content.json_combatant_compiler import (
    compile_hero_definition,
    fold_hero_level,
    load_hero_build,
    load_hero_progression,
    load_hero_track,
    load_species,
    load_subclass_progression,
)


ROOT = Path(__file__).resolve().parents[2]


def _sources():
    progression = load_hero_progression(ROOT / "data/heroes/2024/class_progressions/fighter.json")
    subclass = load_subclass_progression(ROOT / "data/heroes/2024/subclasses/champion.json")
    species = load_species(ROOT / "data/heroes/2024/species/orc.json")
    track = load_hero_track(ROOT / "data/heroes/2024/tracks/karnok-stoneward.json")
    build = load_hero_build(ROOT / "data/heroes/2024/builds/karnok-stoneward.json")
    return progression, subclass, species, track, build


def _fold(level: int):
    progression, subclass, species, track, build = _sources()
    folded = fold_hero_level(progression, subclass, species, track, level)
    return folded, build


def test_fighter_json_compiles_through_same_definition_boundary_as_monsters():
    folded, build = _fold(3)
    definition = compile_hero_definition("karnok-stoneward", "Karnok Stoneward", folded, build)
    template = compile_combatant(definition)

    assert definition.kind == "character"
    assert template.kind == "character"
    assert template.id == "karnok-stoneward-l3"
    assert template.ability_scores.strength == 17
    assert template.weapon_attack.attack_bonus == 5
    assert template.weapon_attack.damage_bonus == 3
    assert template.progression_features.critical_hit_minimum == 19


def test_fighter_json_derives_attack_math_after_asi():
    folded, build = _fold(4)
    template = compile_combatant(
        compile_hero_definition("karnok-stoneward", "Karnok Stoneward", folded, build)
    )

    assert template.ability_scores.strength == 18
    assert template.weapon_attack.attack_bonus == 6
    assert template.weapon_attack.damage_bonus == 4
    assert template.saving_throw_bonuses["strength"] == 6


def test_level_eighteen_survivor_compiles_through_shared_boundary():
    folded, build = _fold(18)
    definition = compile_hero_definition("karnok-stoneward", "Karnok Stoneward", folded, build)
    template = compile_combatant(definition)

    assert definition.unsupported_capabilities == []
    assert template.progression_features.survivor_heal_amount == 10
    assert template.progression_features.death_save_advantage is True
    assert template.progression_features.death_save_nat20_minimum == 18


def test_character_and_monster_share_engine_facing_template_contract():
    folded, build = _fold(3)
    hero = compile_combatant(
        compile_hero_definition("karnok-stoneward", "Karnok Stoneward", folded, build)
    )
    monster = compile_combatant(get_capability_definition("srd-swarm-of-insects"))

    assert hero.kind == "character"
    assert monster.kind == "monster"
    assert type(hero) is type(monster)
    for field in (
        "ruleset", "armor_class", "max_hp", "speed_ft", "movement_modes",
        "initiative_bonus", "weapon_attack", "alternate_weapon_attacks",
        "attack_action", "saving_throw_actions", "combat_traits",
        "damage_resistances", "condition_immunities", "resources",
    ):
        assert hasattr(hero, field)
        assert hasattr(monster, field)
    assert hero.ruleset == monster.ruleset == "2024"


def test_hero_build_rejects_cross_edition_compilation():
    folded, build = _fold(3)
    mismatched = build.model_copy(update={"edition": "2014"})

    with pytest.raises(ValueError, match="share edition and class"):
        compile_hero_definition("karnok-stoneward", "Karnok Stoneward", folded, mismatched)


def test_fold_rejects_species_edition_mismatch():
    progression, subclass, species, track, _build = _sources()
    mismatched = species.model_copy(update={"edition": "2014"})
    with pytest.raises(ValueError, match="Species must share edition"):
        fold_hero_level(progression, subclass, mismatched, track, 3)

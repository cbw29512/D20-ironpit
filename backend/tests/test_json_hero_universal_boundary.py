from pathlib import Path

import pytest

from app.content.capability_attack_compiler import UnsupportedCapabilityError
from app.content.capability_compiler import compile_combatant
from app.content.capability_registry import get_capability_definition
from app.content.json_combatant_compiler import (
    compile_hero_definition,
    fold_hero_level,
    load_hero_build,
    load_hero_progression,
    load_subclass_progression,
)


ROOT = Path(__file__).resolve().parents[2]


def _sources():
    progression = load_hero_progression(ROOT / "data/heroes/2024/class_progressions/fighter.json")
    subclass = load_subclass_progression(ROOT / "data/heroes/2024/subclasses/champion.json")
    build = load_hero_build(ROOT / "data/heroes/2024/builds/karnok-stoneward.json")
    return progression, subclass, build


def test_fighter_json_compiles_through_same_definition_boundary_as_monsters():
    progression, subclass, build = _sources()
    folded = fold_hero_level(progression, subclass, 3)
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
    progression, subclass, build = _sources()
    folded = fold_hero_level(progression, subclass, 4)
    template = compile_combatant(
        compile_hero_definition("karnok-stoneward", "Karnok Stoneward", folded, build)
    )

    assert template.ability_scores.strength == 18
    assert template.weapon_attack.attack_bonus == 6
    assert template.weapon_attack.damage_bonus == 4
    assert template.saving_throw_bonuses["strength"] == 6


def test_unsupported_high_level_capability_fails_closed_at_shared_compiler():
    progression, subclass, build = _sources()
    folded = fold_hero_level(progression, subclass, 18)
    definition = compile_hero_definition("karnok-stoneward", "Karnok Stoneward", folded, build)

    assert "survivor-defy-death" in definition.unsupported_capabilities
    with pytest.raises(UnsupportedCapabilityError):
        compile_combatant(definition)


def test_character_and_monster_share_engine_facing_template_contract():
    progression, subclass, build = _sources()
    hero = compile_combatant(
        compile_hero_definition(
            "karnok-stoneward",
            "Karnok Stoneward",
            fold_hero_level(progression, subclass, 3),
            build,
        )
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
    progression, subclass, build = _sources()
    folded = fold_hero_level(progression, subclass, 3)
    mismatched = build.model_copy(update={"edition": "2014"})

    with pytest.raises(ValueError, match="share edition and class"):
        compile_hero_definition("karnok-stoneward", "Karnok Stoneward", folded, mismatched)

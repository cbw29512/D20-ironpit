from pathlib import Path

import pytest

from app.content.capability_attack_compiler import UnsupportedCapabilityError
from app.content.capability_compiler import compile_combatant
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

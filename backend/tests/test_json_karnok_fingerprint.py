from pathlib import Path

from app.content.capability_compiler import compile_combatant
from app.content.fighter_progression import build_karnok_stoneward_level
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
CERTIFIED_2024_FIGHTER_LEVELS = range(1, 15)
SKIP = {"source", "visual"}


def _sources():
    return (
        load_hero_progression(ROOT / "data/heroes/2024/class_progressions/fighter.json"),
        load_subclass_progression(ROOT / "data/heroes/2024/subclasses/champion.json"),
        load_species(ROOT / "data/heroes/2024/species/orc.json"),
        load_hero_track(ROOT / "data/heroes/2024/tracks/karnok-stoneward.json"),
        load_hero_build(ROOT / "data/heroes/2024/builds/karnok-stoneward.json"),
    )


def _json_template(level: int):
    progression, subclass, species, track, build = _sources()
    folded = fold_hero_level(progression, subclass, species, track, level)
    return compile_combatant(
        compile_hero_definition("karnok-stoneward", "Karnok Stoneward", folded, build)
    )


def _diff(left, right, path=""):
    diffs = []
    if isinstance(left, dict) and isinstance(right, dict):
        for key in sorted(set(left) | set(right)):
            if key in SKIP:
                continue
            diffs.extend(_diff(left.get(key), right.get(key), f"{path}.{key}" if path else key))
        return diffs
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            diffs.append((f"{path}#len", len(left), len(right)))
        for index, (item_left, item_right) in enumerate(zip(left, right)):
            diffs.extend(_diff(item_left, item_right, f"{path}[{index}]"))
        return diffs
    if left != right:
        diffs.append((path, left, right))
    return diffs


def test_json_karnok_matches_certified_python_levels_1_through_14():
    mismatches = {}
    for level in CERTIFIED_2024_FIGHTER_LEVELS:
        certified = build_karnok_stoneward_level(level).model_dump(mode="python")
        compiled = _json_template(level).model_dump(mode="python")
        diffs = _diff(certified, compiled)
        if diffs:
            mismatches[level] = diffs
    assert mismatches == {}

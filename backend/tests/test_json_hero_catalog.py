from pathlib import Path

from app.content.capability_compiler import compile_combatant
from app.content.hero_progressions import CANONICAL_HEROES
from app.content.json_combatant_compiler import (
    compile_hero_definition,
    fold_hero_level,
    load_hero_bundle,
    load_hero_catalog,
)


ROOT = Path(__file__).resolve().parents[2]
REMAINING_2014 = {
    "lyra-silverstring-2014",
    "seraphine-dawnshield-2014",
    "thalen-greenbough-2014",
    "rowan-ashtrail-2014",
    "nyra-emberveil-2014",
    "varek-ashenmark-2014",
    "elian-starweaver-2014",
}
REMAINING_2024 = {
    "lyra-silverstring",
    "thalen-greenbough",
    "kael-stillwater",
    "aurelia-brightshield",
    "rowan-ashtrail",
    "nyra-emberveil",
    "varek-ashenmark",
    "elian-starweaver",
}


def test_certified_catalog_heroes_fold_and_compile_every_declared_level():
    for edition in ("2014", "2024"):
        catalog = load_hero_catalog(ROOT / f"data/heroes/{edition}/heroes.json")
        for identity in catalog.heroes:
            _identity, class_prog, subclass, species, track, build = load_hero_bundle(
                ROOT, edition, identity.id
            )
            low, high = identity.level_range
            for level in range(low, high + 1):
                folded = fold_hero_level(class_prog, subclass, species, track, level)
                definition = compile_hero_definition(identity.id, identity.name, folded, build)
                if definition.unsupported_capabilities:
                    continue
                compiled = compile_combatant(definition)
                assert compiled.id == f"{identity.id}-l{level}"
                assert compiled.ruleset == edition
                assert compiled.level == level


def test_2024_class_tables_cover_all_twelve_canonical_classes():
    present = {path.stem for path in (ROOT / "data/heroes/2024/class_progressions").glob("*.json")}
    expected = {hero.class_id for hero in CANONICAL_HEROES}
    assert expected <= present


def test_uncertified_canonical_tracks_are_not_invented():
    catalogs = {
        edition: {item.id for item in load_hero_catalog(ROOT / f"data/heroes/{edition}/heroes.json").heroes}
        for edition in ("2014", "2024")
    }
    assert REMAINING_2014.isdisjoint(catalogs["2014"])
    assert REMAINING_2024.isdisjoint(catalogs["2024"])
    assert {"karnok-stoneward-2014", "rokhan-stonefury-2014", "mara-quickstep-2014",
            "kael-stillwater-2014", "aurelia-brightshield-2014"} <= catalogs["2014"]
    assert {"karnok-stoneward", "rokhan-stonefury", "seraphine-dawnshield", "mara-quickstep"} <= catalogs["2024"]

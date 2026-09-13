from app.content.monster_attack_source_audit import _dice_pattern
from app.content.monster_defense_source_audit import _parse_defense_text, parse_defense_profile
from app.content.monster_registry_build import is_clean, stable_hash
from app.content.monster_trait_source_audit import _parse_trait_names_cached, parse_trait_names


def test_registry_dirty_check_requires_matching_source_compiler_and_entry_hashes() -> None:
    entry = {"id": "srd-killer-whale", "hp": 90}
    source_hash = stable_hash({"id": "srd-killer-whale", "hp": 90})
    compiler_hash = "compiler-v1"
    cache = {
        "pipeline_hash": compiler_hash,
        "entries": {
            "srd-killer-whale": {
                "source_hash": source_hash,
                "entry_hash": stable_hash(entry),
            }
        },
    }
    assert is_clean(
        monster_id="srd-killer-whale",
        source_hash=source_hash,
        entry=entry,
        cache=cache,
        compiler_hash=compiler_hash,
    )
    assert not is_clean(
        monster_id="srd-killer-whale",
        source_hash=stable_hash({"id": "srd-killer-whale", "hp": 91}),
        entry=entry,
        cache=cache,
        compiler_hash=compiler_hash,
    )
    assert not is_clean(
        monster_id="srd-killer-whale",
        source_hash=source_hash,
        entry=entry,
        cache=cache,
        compiler_hash="compiler-v2",
    )


def test_defense_parser_cache_returns_fresh_mutable_sets() -> None:
    row = {"rawText": "Vulnerabilities Fire Resistances Cold Immunities Poisoned Actions Bite."}
    first = parse_defense_profile(row)
    first["damage_vulnerabilities"].add("acid")
    second = parse_defense_profile(row)
    assert second["damage_vulnerabilities"] == {"fire"}
    assert _parse_defense_text.cache_info().hits >= 1


def test_trait_parser_cache_returns_fresh_lists() -> None:
    source = "Pack Tactics. The wolf has Advantage on an attack roll. Keen Hearing. The wolf has Advantage on Wisdom checks."
    first = parse_trait_names(source)
    first.append("Injected")
    second = parse_trait_names(source)
    assert second == ["Pack Tactics", "Keen Hearing"]
    assert _parse_trait_names_cached.cache_info().hits >= 1


def test_dice_regex_is_memoized() -> None:
    before = _dice_pattern.cache_info().hits
    assert _dice_pattern(2, 6, 3) is _dice_pattern(2, 6, 3)
    assert _dice_pattern.cache_info().hits > before

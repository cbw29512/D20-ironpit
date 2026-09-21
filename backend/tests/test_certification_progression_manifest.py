from __future__ import annotations

import json
from pathlib import Path

from app.domain.progression import ProgressionCombatFeatures


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SCRIPT = ROOT / "scripts" / "verify_certification_manifests.py"
HERO_MANIFEST = ROOT / "data" / "hero_certification_manifest.json"
BROWSER_HEROES = ROOT / "frontend" / "browser-heroes.js"


def test_manifest_generator_accounts_for_every_progression_combat_field() -> None:
    source = MANIFEST_SCRIPT.read_text(encoding="utf-8")
    missing = [
        field
        for field in ProgressionCombatFeatures.model_fields
        if f"features.{field}" not in source
    ]
    assert missing == [], f"Progression combat fields missing from certification mechanics: {missing}"


def test_barbarian_level_two_manifest_requires_both_level_two_features() -> None:
    manifest = json.loads(HERO_MANIFEST.read_text(encoding="utf-8"))
    barbarian = next(hero for hero in manifest["heroes"] if hero["class_id"] == "barbarian")
    level_two = next(level for level in barbarian["levels"] if level["level"] == 2)
    required = {"danger-sense", "reckless-attack"}

    assert required <= set(level_two["expected_combat_features"])
    assert required <= set(level_two["supported_mechanics"])
    assert level_two["unsupported_mechanics"] == []
    assert level_two["public_ready_status"] == "ready"


def test_barbarian_level_three_manifest_requires_frenzy() -> None:
    manifest = json.loads(HERO_MANIFEST.read_text(encoding="utf-8"))
    barbarian = next(hero for hero in manifest["heroes"] if hero["class_id"] == "barbarian")
    level_three = next(level for level in barbarian["levels"] if level["level"] == 3)

    assert "frenzy" in level_three["expected_combat_features"]
    assert "frenzy" in level_three["supported_mechanics"]
    assert level_three["unsupported_mechanics"] == []
    assert level_three["public_ready_status"] == "ready"


def test_fighter_level_eight_manifest_preserves_gwf_and_extra_attack_without_blockers() -> None:
    manifest = json.loads(HERO_MANIFEST.read_text(encoding="utf-8"))
    fighter = next(hero for hero in manifest["heroes"] if hero["class_id"] == "fighter")
    level_eight = next(level for level in fighter["levels"] if level["level"] == 8)
    required = {"great-weapon-fighting", "multiattack-or-extra-attack", "expanded-critical-range"}

    assert required <= set(level_eight["expected_combat_features"])
    assert required <= set(level_eight["supported_mechanics"])
    assert level_eight["unsupported_mechanics"] == []
    assert level_eight["blockers"] == []
    assert level_eight["public_ready_status"] == "ready"


def test_fighter_levels_thirteen_through_seventeen_are_public() -> None:
    manifest = json.loads(HERO_MANIFEST.read_text(encoding="utf-8"))
    fighter = next(hero for hero in manifest["heroes"] if hero["class_id"] == "fighter")
    levels = {level["level"]: level for level in fighter["levels"]}
    counted_ready = sum(
        1
        for hero in manifest["heroes"]
        for level in hero["levels"]
        if level["public_ready_status"] == "ready"
    )
    required_thirteen = {
        "heroic-warrior", "indomitable", "studied-attacks", "tactical-master",
        "great-weapon-fighting", "multiattack-or-extra-attack",
    }
    browser = BROWSER_HEROES.read_text(encoding="utf-8")

    assert manifest["summary"]["public_ready"] == counted_ready == 29

    for level_number in (13, 14, 15, 16, 17):
        level = levels[level_number]
        assert level["runtime_template_id"] == f"karnok-stoneward-l{level_number}"
        assert required_thirteen <= set(level["expected_combat_features"])
        assert required_thirteen <= set(level["supported_mechanics"])
        assert level["unsupported_mechanics"] == []
        assert level["blockers"] == []
        assert level["public_ready_status"] == "ready"
        assert f"karnok-stoneward-l{level_number}" in browser

    for level_number in (15, 16, 17):
        level = levels[level_number]
        assert "expanded-critical-range" in level["expected_combat_features"]
        assert "expanded-critical-range" in level["supported_mechanics"]

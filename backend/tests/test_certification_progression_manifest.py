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


def test_fighter_full_progression_is_public_and_manifest_count_is_self_consistent() -> None:
    manifest = json.loads(HERO_MANIFEST.read_text(encoding="utf-8"))
    fighter = next(hero for hero in manifest["heroes"] if hero["class_id"] == "fighter")
    level_twelve = next(level for level in fighter["levels"] if level["level"] == 12)
    level_thirteen = next(level for level in fighter["levels"] if level["level"] == 13)
    level_twenty = next(level for level in fighter["levels"] if level["level"] == 20)
    counted_ready = sum(
        1
        for hero in manifest["heroes"]
        for level in hero["levels"]
        if level["public_ready_status"] == "ready"
    )
    required = {
        "heroic-warrior", "indomitable", "tactical-master",
        "great-weapon-fighting", "multiattack-or-extra-attack",
    }
    browser = BROWSER_HEROES.read_text(encoding="utf-8")

    assert manifest["summary"]["public_ready"] == counted_ready
    assert counted_ready >= 36
    assert level_twelve["runtime_template_id"] == "karnok-stoneward-l12"
    assert required <= set(level_twelve["expected_combat_features"])
    assert required <= set(level_twelve["supported_mechanics"])
    assert level_twelve["unsupported_mechanics"] == []
    assert level_twelve["blockers"] == []
    assert level_twelve["public_ready_status"] == "ready"
    assert "karnok-stoneward-l12" in browser

    assert level_thirteen["runtime_template_id"] == "karnok-stoneward-l13"
    assert level_thirteen["public_ready_status"] == "ready"
    assert level_thirteen["blockers"] == []
    assert "karnok-stoneward-l13" in browser
    assert level_twenty["runtime_template_id"] == "karnok-stoneward-l20"
    assert level_twenty["public_ready_status"] == "ready"
    assert "karnok-stoneward-l20" in browser

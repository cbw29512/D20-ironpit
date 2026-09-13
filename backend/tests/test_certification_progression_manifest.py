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


def test_fighter_levels_eighteen_through_twenty_are_public() -> None:
    manifest = json.loads(HERO_MANIFEST.read_text(encoding="utf-8"))
    fighter = next(hero for hero in manifest["heroes"] if hero["class_id"] == "fighter")
    level_seventeen = next(level for level in fighter["levels"] if level["level"] == 17)
    level_eighteen = next(level for level in fighter["levels"] if level["level"] == 18)
    level_nineteen = next(level for level in fighter["levels"] if level["level"] == 19)
    level_twenty = next(level for level in fighter["levels"] if level["level"] == 20)
    counted_ready = sum(
        1
        for hero in manifest["heroes"]
        for level in hero["levels"]
        if level["public_ready_status"] == "ready"
    )
    level_seventeen_required = {
        "heroic-warrior", "indomitable", "tactical-master", "studied-attacks",
        "expanded-critical-range", "great-weapon-fighting", "multiattack-or-extra-attack",
    }
    level_eighteen_required = {
        *level_seventeen_required,
        "survivor-defy-death",
        "survivor-heroic-rally",
    }
    level_nineteen_required = {*level_eighteen_required, "boon-combat-prowess"}
    level_twenty_required = {*level_nineteen_required, "extra-attack-4"}
    browser = BROWSER_HEROES.read_text(encoding="utf-8")

    assert manifest["summary"]["public_ready"] == counted_ready == 34
    assert level_seventeen["runtime_template_id"] == "karnok-stoneward-l17"
    assert level_seventeen_required <= set(level_seventeen["expected_combat_features"])
    assert level_seventeen_required <= set(level_seventeen["supported_mechanics"])
    assert level_seventeen["unsupported_mechanics"] == []
    assert level_seventeen["blockers"] == []
    assert level_seventeen["public_ready_status"] == "ready"
    assert "karnok-stoneward-l17" in browser

    assert level_eighteen["runtime_template_id"] == "karnok-stoneward-l18"
    assert level_eighteen_required <= set(level_eighteen["expected_combat_features"])
    assert level_eighteen_required <= set(level_eighteen["supported_mechanics"])
    assert level_eighteen["unsupported_mechanics"] == []
    assert level_eighteen["blockers"] == []
    assert level_eighteen["public_ready_status"] == "ready"
    assert "karnok-stoneward-l18" in browser

    assert level_nineteen["runtime_template_id"] == "karnok-stoneward-l19"
    assert level_nineteen_required <= set(level_nineteen["expected_combat_features"])
    assert level_nineteen_required <= set(level_nineteen["supported_mechanics"])
    assert level_nineteen["unsupported_mechanics"] == []
    assert level_nineteen["blockers"] == []
    assert level_nineteen["public_ready_status"] == "ready"
    assert "karnok-stoneward-l19" in browser

    assert level_twenty["runtime_template_id"] == "karnok-stoneward-l20"
    assert level_twenty_required <= set(level_twenty["expected_combat_features"])
    assert level_twenty_required <= set(level_twenty["supported_mechanics"])
    assert level_twenty["unsupported_mechanics"] == []
    assert level_twenty["blockers"] == []
    assert level_twenty["public_ready_status"] == "ready"
    assert "karnok-stoneward-l20" in browser

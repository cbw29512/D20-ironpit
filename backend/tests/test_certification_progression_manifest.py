from __future__ import annotations

import json
from pathlib import Path

from app.domain.progression import ProgressionCombatFeatures


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SCRIPT = ROOT / "scripts" / "verify_certification_manifests.py"
HERO_MANIFEST = ROOT / "data" / "hero_certification_manifest.json"


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

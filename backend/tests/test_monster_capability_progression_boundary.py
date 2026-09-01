from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPORTER = ROOT / "scripts" / "export_runtime_monster_capabilities.py"
REGISTRY = ROOT / "backend" / "app" / "content" / "data" / "combatant_capabilities_v1.json"
HERO_ONLY_FIELDS = {"danger_sense", "reckless_attack", "frenzy"}


def test_monster_export_explicitly_excludes_hero_only_progression_fields() -> None:
    source = EXPORTER.read_text(encoding="utf-8")
    for field in HERO_ONLY_FIELDS:
        assert f'"{field}"' in source, f"Monster capability exporter must explicitly exclude {field}."


def test_checked_in_monster_registry_does_not_serialize_hero_only_progression_fields() -> None:
    registry = REGISTRY.read_text(encoding="utf-8")
    for field in HERO_ONLY_FIELDS:
        assert f'"{field}"' not in registry, f"Hero-only progression field leaked into monster registry: {field}."

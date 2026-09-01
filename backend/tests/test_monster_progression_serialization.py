import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPORTER = ROOT / "scripts" / "export_runtime_monster_capabilities.py"
HERO_ONLY_FIELDS = {"danger_sense", "reckless_attack", "frenzy", "fast_movement_bonus_ft"}


def _load_exporter():
    spec = importlib.util.spec_from_file_location("runtime_monster_capability_exporter", EXPORTER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load runtime monster capability exporter.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_monster_capability_export_excludes_all_hero_only_progression_fields() -> None:
    module = _load_exporter()
    assert HERO_ONLY_FIELDS <= module._HERO_ONLY_PROGRESSION_FIELDS
    rows = json.loads(module.render_registry())
    assert rows
    for row in rows:
        progression = row.get("progression_features", {})
        assert HERO_ONLY_FIELDS.isdisjoint(progression), row["id"]

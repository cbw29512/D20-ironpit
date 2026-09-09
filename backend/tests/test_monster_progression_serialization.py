import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPORTER = ROOT / "scripts" / "export_runtime_monster_capabilities.py"
HERO_ONLY_FIELDS = {
    "danger_sense", "reckless_attack", "frenzy", "fast_movement_bonus_ft", "mindless_rage",
    "instinctive_pounce_fraction", "great_weapon_fighting", "indomitable_bonus",
    "tactical_master_sap_weapon_ids",
}


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


def test_monster_capability_export_omits_semantically_empty_effect_gates() -> None:
    module = _load_exporter()
    rows = json.loads(module.render_registry())
    for row in rows:
        for action in [*row.get("attacks", []), *row.get("save_actions", [])]:
            grapple = action.get("grapple")
            if isinstance(grapple, dict):
                assert "gate" not in grapple, (row["id"], action["id"])
            for effect in action.get("effects", []):
                if not isinstance(effect, dict):
                    continue
                gate = effect.get("gate")
                if not isinstance(gate, dict):
                    continue
                assert any((
                    gate.get("required_target_tags"),
                    gate.get("excluded_target_tags"),
                    gate.get("excluded_creature_types"),
                    gate.get("save_ability"),
                )), (row["id"], action["id"], effect.get("kind"))

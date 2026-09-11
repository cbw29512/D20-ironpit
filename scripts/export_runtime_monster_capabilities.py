from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_registry_build import (
    compile_payloads,
    is_clean,
    load_cache,
    pipeline_hash,
    stable_hash,
    template_payload,
    write_cache,
)

logger = logging.getLogger(__name__)
_OUTPUT = Path("backend/app/content/data/combatant_capabilities_v1.json")
_HERO_ONLY_PROGRESSION_FIELDS = {
    "danger_sense", "reckless_attack", "frenzy", "fast_movement_bonus_ft", "mindless_rage",
    "instinctive_pounce_fraction", "great_weapon_fighting", "indomitable_bonus",
    "tactical_master_sap_weapon_ids", "sneak_attack_d6",
}
_EXCLUDE = {
    "progression_features": _HERO_ONLY_PROGRESSION_FIELDS,
    "movement_modes": {"pass_through_creatures_as_difficult_terrain"},
}


def _load_existing() -> list[dict[str, object]]:
    try:
        if not _OUTPUT.exists():
            return []
        payload = json.loads(_OUTPUT.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise RuntimeError("Combat capability registry must contain a JSON list.")
        return payload
    except Exception:
        logger.exception("Failed to load existing monster capability registry.")
        raise


def _matches_selector(monster_id: str, selector: str | None) -> bool:
    try:
        if selector is None:
            return True
        normalized = selector.strip().lower().replace("_", "-")
        current = monster_id.lower()
        return current == normalized or current == f"srd-{normalized}"
    except Exception:
        logger.exception("Failed to evaluate monster selector %r.", selector)
        raise


def _build_registry(*, selector: str | None = None, jobs: int = 0, force: bool = False) -> tuple[str, dict[str, dict[str, str]], int, int]:
    try:
        monsters = build_legacy_monster_templates()
        ids = [monster.id for monster in monsters]
        if len(ids) != len(set(ids)):
            raise RuntimeError("Legacy runtime monster ids must be unique before capability export.")
        selected = [monster for monster in monsters if _matches_selector(monster.id, selector)]
        if selector is not None and len(selected) != 1:
            raise RuntimeError(f"Monster selector {selector!r} matched {len(selected)} runtime templates; expected exactly one.")

        existing_rows = _load_existing()
        existing = {str(row["id"]): row for row in existing_rows}
        if selector is not None and not existing_rows:
            raise RuntimeError("Targeted export requires an existing full registry to preserve untouched monsters.")
        cache = load_cache()
        compiler_hash = pipeline_hash()
        payloads = {monster.id: template_payload(monster) for monster in monsters}
        source_hashes = {monster_id: stable_hash(payload) for monster_id, payload in payloads.items()}

        dirty_ids: list[str] = []
        for monster in selected:
            clean = is_clean(
                monster_id=monster.id,
                source_hash=source_hashes[monster.id],
                entry=existing.get(monster.id),
                cache=cache,
                compiler_hash=compiler_hash,
            )
            if force or selector is not None or not clean:
                dirty_ids.append(monster.id)
        compiled = compile_payloads([payloads[monster_id] for monster_id in dirty_ids], _EXCLUDE, jobs)
        for monster_id, row in zip(dirty_ids, compiled, strict=True):
            existing[monster_id] = row

        missing = [monster_id for monster_id in ids if monster_id not in existing]
        if missing:
            raise RuntimeError(f"Registry build is missing {len(missing)} templates; first missing id: {missing[0]}.")
        rows = [existing[monster_id] for monster_id in ids]
        entries = {
            monster_id: {"source_hash": source_hashes[monster_id], "entry_hash": stable_hash(existing[monster_id])}
            for monster_id in ids
        }
        rendered = json.dumps(rows, indent=2, sort_keys=False) + "\n"
        return rendered, entries, len(dirty_ids), len(ids) - len(dirty_ids)
    except Exception:
        logger.exception("Monster capability registry build failed.")
        raise


def render_registry() -> str:
    try:
        rendered, _, _, _ = _build_registry(force=True)
        return rendered
    except Exception:
        logger.exception("Deterministic full monster registry render failed.")
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the legacy monster runtime into capability data.")
    parser.add_argument("--check", action="store_true", help="Fail if the checked-in registry is stale.")
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--slug", help="Compile only one monster slug and preserve all other registry entries.")
    selector.add_argument("--id", dest="monster_id", help="Compile only one exact runtime monster id.")
    parser.add_argument("--jobs", type=int, default=0, help="Worker processes for dirty templates; 0 uses executor default.")
    parser.add_argument("--force", action="store_true", help="Ignore dirty-state cache and rebuild selected templates.")
    args = parser.parse_args()
    try:
        target = args.slug or args.monster_id
        rendered, entries, compiled, reused = _build_registry(selector=target, jobs=args.jobs, force=args.force)
        if args.check:
            if not _OUTPUT.exists() or _OUTPUT.read_text(encoding="utf-8") != rendered:
                raise RuntimeError("Combat capability registry is stale; regenerate it before committing.")
            print(f"Capability registry is deterministic and current: {_OUTPUT} ({compiled} compiled, {reused} reused).")
            return
        _OUTPUT.write_text(rendered, encoding="utf-8")
        write_cache(entries, pipeline_hash())
        print(f"Exported {len(entries)} capability definitions to {_OUTPUT} ({compiled} compiled, {reused} reused).")
    except Exception:
        logger.exception("Runtime monster capability export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

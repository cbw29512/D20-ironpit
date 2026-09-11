from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
import logging
from pathlib import Path
from typing import Any

from app.content.capability_from_template import definition_from_template
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[3]
CACHE_PATH = ROOT / ".cache" / "ironpit" / "monster_registry_state.json"
PIPELINE_FILES = (
    ROOT / "backend" / "app" / "content" / "capability_from_template.py",
    ROOT / "backend" / "app" / "domain" / "capabilities.py",
)


def stable_hash(value: object) -> str:
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return sha256(encoded).hexdigest()
    except Exception:
        logger.exception("Failed to hash monster registry build value.")
        raise


def pipeline_hash() -> str:
    try:
        digest = sha256()
        for path in PIPELINE_FILES:
            digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
            digest.update(path.read_bytes())
        return digest.hexdigest()
    except Exception:
        logger.exception("Failed to hash monster registry compiler pipeline.")
        raise


def template_payload(template: CombatantTemplate) -> dict[str, Any]:
    try:
        return template.model_dump(mode="json")
    except Exception:
        logger.exception("Failed to serialize monster template %s.", getattr(template, "id", "<unknown>"))
        raise


def normalize_definition(row: dict[str, Any]) -> dict[str, Any]:
    try:
        for action in row.get("save_actions", []):
            if action.get("action_cost") == "action":
                action.pop("action_cost")
            if action.get("required_target_condition") is None:
                action.pop("required_target_condition", None)
        return row
    except Exception:
        logger.exception("Failed to normalize compiled monster definition.")
        raise


def compile_payload(payload: dict[str, Any], exclude: dict[str, object]) -> dict[str, Any]:
    try:
        template = CombatantTemplate.model_validate(payload)
        definition = definition_from_template(template)
        return normalize_definition(definition.model_dump(mode="json", exclude_none=True, exclude=exclude))
    except Exception:
        logger.exception("Failed to compile monster template %s.", payload.get("id", "<unknown>"))
        raise


def compile_payloads(payloads: list[dict[str, Any]], exclude: dict[str, object], jobs: int) -> list[dict[str, Any]]:
    try:
        if len(payloads) < 2 or jobs == 1:
            return [compile_payload(payload, exclude) for payload in payloads]
        max_workers = None if jobs <= 0 else jobs
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(compile_payload, payloads, [exclude] * len(payloads)))
    except Exception:
        logger.exception("Parallel monster registry compilation failed for %d payloads.", len(payloads))
        raise


def load_cache() -> dict[str, Any]:
    try:
        if not CACHE_PATH.exists():
            return {"pipeline_hash": "", "entries": {}}
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        logger.exception("Failed to read monster registry build cache; forcing a clean rebuild.")
        return {"pipeline_hash": "", "entries": {}}


def write_cache(entries: dict[str, dict[str, str]], compiler_hash: str) -> None:
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {"pipeline_hash": compiler_hash, "entries": entries}
        CACHE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception:
        logger.exception("Failed to write monster registry build cache.")
        raise


def is_clean(*, monster_id: str, source_hash: str, entry: dict[str, Any] | None, cache: dict[str, Any], compiler_hash: str) -> bool:
    try:
        if entry is None or cache.get("pipeline_hash") != compiler_hash:
            return False
        cached = cache.get("entries", {}).get(monster_id, {})
        return cached.get("source_hash") == source_hash and cached.get("entry_hash") == stable_hash(entry)
    except Exception:
        logger.exception("Failed dirty-state check for %s.", monster_id)
        raise

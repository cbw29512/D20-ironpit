from __future__ import annotations

from functools import lru_cache
import json
import logging
from pathlib import Path

from app.content.capability_compiler import compile_combatant
from app.content.monster_creature_types import complete_monster_creature_types
from app.content.monster_recharge_batch import build_recharge_monster_definitions
from app.domain.capabilities import CombatantDefinition
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_DATA_DIR = Path(__file__).with_name("data")
_GENERATED_PATH = _DATA_DIR / "combatant_capabilities_v1.json"
_NATIVE_PATH_GLOB = "combatant_capabilities_native_*.json"


def parse_capability_definitions(rows: object) -> dict[str, CombatantDefinition]:
    if not isinstance(rows, list):
        raise ValueError("Combat capability registry must be a JSON list.")
    definitions = [CombatantDefinition.model_validate(row) for row in rows]
    by_id = {definition.id: definition for definition in definitions}
    if len(by_id) != len(definitions):
        raise ValueError("Combat capability registry ids must be unique.")
    return by_id


def merge_capability_definitions(
    generated: dict[str, CombatantDefinition],
    native: dict[str, CombatantDefinition],
) -> dict[str, CombatantDefinition]:
    overlap = set(generated) & set(native)
    if overlap:
        duplicate = ", ".join(sorted(overlap))
        raise ValueError(f"Generated and native combat capability ids overlap: {duplicate}.")
    return {**generated, **native}


def _load_registry(path: Path) -> dict[str, CombatantDefinition]:
    return parse_capability_definitions(json.loads(path.read_text(encoding="utf-8")))


def _merge_native(
    merged: dict[str, CombatantDefinition],
    shard: dict[str, CombatantDefinition],
    label: str,
) -> None:
    overlap = set(merged) & set(shard)
    if overlap:
        duplicate = ", ".join(sorted(overlap))
        raise ValueError(f"Native combat capability ids overlap in {label}: {duplicate}.")
    merged.update(shard)


def _load_native_registries() -> dict[str, CombatantDefinition]:
    try:
        paths = sorted(_DATA_DIR.glob(_NATIVE_PATH_GLOB))
        if not paths:
            raise ValueError("No native combat capability registry shards were found.")
        merged: dict[str, CombatantDefinition] = {}
        for path in paths:
            _merge_native(merged, _load_registry(path), path.name)
        _merge_native(merged, build_recharge_monster_definitions(), "recharge family")
        return merged
    except Exception:
        logger.exception("Failed to load native combat capability registry shards.")
        raise


@lru_cache(maxsize=1)
def load_capability_definitions() -> dict[str, CombatantDefinition]:
    try:
        generated = _load_registry(_GENERATED_PATH)
        native = _load_native_registries()
        return merge_capability_definitions(generated, native)
    except Exception as exc:
        logger.exception("Failed to load declarative combat capability registries.")
        raise RuntimeError("Combat capability registry could not be loaded.") from exc


def get_capability_definition(combatant_id: str) -> CombatantDefinition:
    definition = load_capability_definitions().get(combatant_id)
    if definition is None:
        raise ValueError(f"No declarative combat capability definition for {combatant_id!r}.")
    return definition


def build_combatant_from_capabilities(combatant_id: str) -> CombatantTemplate:
    template = compile_combatant(get_capability_definition(combatant_id))
    return complete_monster_creature_types([template])[0]


def build_monster_templates_from_capabilities() -> list[CombatantTemplate]:
    try:
        definitions = load_capability_definitions().values()
        monsters = [compile_combatant(item) for item in definitions if item.kind == "monster"]
        if not monsters:
            raise ValueError("Combat capability registry contains no monsters.")
        return complete_monster_creature_types(monsters)
    except Exception as exc:
        logger.exception("Failed to compile monster roster from combat capability registry.")
        raise RuntimeError("Declarative monster roster could not be created.") from exc

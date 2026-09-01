from __future__ import annotations

from functools import lru_cache
import json
import logging
from pathlib import Path

from app.content.capability_compiler import compile_combatant
from app.domain.capabilities import CombatantDefinition
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_DATA_PATH = Path(__file__).with_name("data") / "combatant_capabilities_v1.json"


def parse_capability_definitions(rows: object) -> dict[str, CombatantDefinition]:
    if not isinstance(rows, list):
        raise ValueError("Combat capability registry must be a JSON list.")
    definitions = [CombatantDefinition.model_validate(row) for row in rows]
    by_id = {definition.id: definition for definition in definitions}
    if len(by_id) != len(definitions):
        raise ValueError("Combat capability registry ids must be unique.")
    return by_id


@lru_cache(maxsize=1)
def load_capability_definitions() -> dict[str, CombatantDefinition]:
    try:
        rows = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
        return parse_capability_definitions(rows)
    except Exception as exc:
        logger.exception("Failed to load declarative combat capability registry.")
        raise RuntimeError("Combat capability registry could not be loaded.") from exc


def get_capability_definition(combatant_id: str) -> CombatantDefinition:
    definition = load_capability_definitions().get(combatant_id)
    if definition is None:
        raise ValueError(f"No declarative combat capability definition for {combatant_id!r}.")
    return definition


def build_combatant_from_capabilities(combatant_id: str) -> CombatantTemplate:
    return compile_combatant(get_capability_definition(combatant_id))

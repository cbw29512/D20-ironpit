from __future__ import annotations

from functools import lru_cache
import json
import logging
from pathlib import Path

from app.content.capability_compiler import compile_combatant
from app.content.capability_registry import parse_capability_definitions
from app.domain.capabilities import CombatantDefinition
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_DATA_PATH = Path(__file__).with_name("data") / "combatant_capabilities_2014_mvp_v1.json"
_EXPECTED_IDS = {"2014-bandit", "2014-skeleton"}


@lru_cache(maxsize=1)
def load_2014_mvp_definitions() -> dict[str, CombatantDefinition]:
    try:
        definitions = parse_capability_definitions(
            json.loads(_DATA_PATH.read_text(encoding="utf-8"))
        )
        if set(definitions) != _EXPECTED_IDS:
            raise ValueError("2014 MVP capability slice must contain only Bandit and Skeleton.")
        if any(item.kind != "monster" or item.ruleset != "2014" for item in definitions.values()):
            raise ValueError("2014 MVP capability slice must contain only 2014 monsters.")
        return definitions
    except Exception as exc:
        logger.exception("Failed to load isolated 2014 MVP capability slice.")
        raise RuntimeError("2014 MVP capability slice could not be loaded.") from exc


def build_2014_mvp_monsters() -> list[CombatantTemplate]:
    try:
        return [compile_combatant(item) for item in load_2014_mvp_definitions().values()]
    except Exception as exc:
        logger.exception("Failed to compile isolated 2014 MVP monsters.")
        raise RuntimeError("2014 MVP monsters could not be compiled.") from exc

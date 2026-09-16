from __future__ import annotations

from functools import lru_cache
import logging

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import is_basic_candidate_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.capabilities import CombatantDefinition
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_basic_2014_definitions() -> dict[str, CombatantDefinition]:
    try:
        definitions = {
            definition.id: definition
            for monster in load_monster_source_2014()
            if is_basic_candidate_2014(monster)
            for definition in [adapt_basic_monster_2014(monster)]
        }
        if len(definitions) <= 4:
            raise ValueError("Bulk 2014 roster must improve on the four-monster MVP slice.")
        if any(item.ruleset != "2014" or item.kind != "monster" for item in definitions.values()):
            raise ValueError("Bulk 2014 roster contains a non-2014 monster definition.")
        return definitions
    except Exception as exc:
        logger.exception("Failed to build the fail-closed 2014 basic definition roster.")
        raise RuntimeError("2014 basic definition roster could not be built.") from exc


@lru_cache(maxsize=1)
def build_basic_2014_monsters() -> tuple[CombatantTemplate, ...]:
    try:
        return tuple(compile_combatant(item) for item in load_basic_2014_definitions().values())
    except Exception as exc:
        logger.exception("Failed to compile the fail-closed 2014 basic monster roster.")
        raise RuntimeError("2014 basic monster roster could not be compiled.") from exc

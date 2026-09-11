from __future__ import annotations

from functools import lru_cache
import json
import logging
from pathlib import Path

from app.content.capability_compiler import compile_combatant
from app.content.monster_aura_source import complete_monster_end_turn_damage_auras
from app.content.monster_creature_types import complete_monster_creature_types
from app.content.monster_trait_source_audit import complete_monster_trait_fingerprints
from app.domain.capabilities import CombatantDefinition
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_DATA_DIR = Path(__file__).with_name("data")
_GENERATED_PATH = _DATA_DIR / "combatant_capabilities_v1.json"
_NATIVE_PATH = _DATA_DIR / "combatant_capabilities_native_v1.json"
_INCREMENTAL_PATH = _DATA_DIR / "combatant_capabilities_incremental_v1.json"
_RECHARGE_PATH = _DATA_DIR / "combatant_capabilities_recharge_v1.json"
_RECHARGE_BATCH3_PATH = _DATA_DIR / "combatant_capabilities_recharge_batch3_v1.json"
_RIDERS_PATH = _DATA_DIR / "combatant_capabilities_riders_v1.json"
_TRAITS_PATH = _DATA_DIR / "combatant_capabilities_traits_v1.json"


def parse_capability_definitions(rows: object) -> dict[str, CombatantDefinition]:
    if not isinstance(rows, list):
        raise ValueError("Combat capability registry must be a JSON list.")
    definitions = [CombatantDefinition.model_validate(row) for row in rows]
    by_id = {definition.id: definition for definition in definitions}
    if len(by_id) != len(definitions):
        raise ValueError("Combat capability registry ids must be unique.")
    missing_unarmed = [
        definition.id
        for definition in definitions
        if definition.kind == "monster" and definition.unarmed_opportunity_attack is None
    ]
    if missing_unarmed:
        raise ValueError(
            "Monster capability definitions require certified unarmed opportunity profiles: "
            + ", ".join(sorted(missing_unarmed))
        )
    return by_id


def merge_capability_definitions(
    generated: dict[str, CombatantDefinition],
    native: dict[str, CombatantDefinition],
) -> dict[str, CombatantDefinition]:
    overlap = set(generated) & set(native)
    if overlap:
        duplicate = ", ".join(sorted(overlap))
        raise ValueError(f"Combat capability registry ids overlap: {duplicate}.")
    return {**generated, **native}


def _load_registry(path: Path) -> dict[str, CombatantDefinition]:
    return parse_capability_definitions(json.loads(path.read_text(encoding="utf-8")))


@lru_cache(maxsize=1)
def load_capability_definitions() -> dict[str, CombatantDefinition]:
    try:
        registries = [
            _load_registry(_GENERATED_PATH),
            _load_registry(_NATIVE_PATH),
            _load_registry(_INCREMENTAL_PATH),
            _load_registry(_RECHARGE_PATH),
            _load_registry(_RECHARGE_BATCH3_PATH),
            _load_registry(_RIDERS_PATH),
            _load_registry(_TRAITS_PATH),
        ]
        merged: dict[str, CombatantDefinition] = {}
        for registry in registries:
            merged = merge_capability_definitions(merged, registry)
        return merged
    except Exception as exc:
        logger.exception("Failed to load declarative combat capability registries.")
        raise RuntimeError("Combat capability registry could not be loaded.") from exc


def get_capability_definition(combatant_id: str) -> CombatantDefinition:
    definition = load_capability_definitions().get(combatant_id)
    if definition is None:
        raise ValueError(f"No declarative combat capability definition for {combatant_id!r}.")
    return definition


def _complete_monster(template: CombatantTemplate) -> CombatantTemplate:
    completed = complete_monster_creature_types([template])
    completed = complete_monster_end_turn_damage_auras(completed)
    return complete_monster_trait_fingerprints(completed)[0]


def build_combatant_from_capabilities(combatant_id: str) -> CombatantTemplate:
    return _complete_monster(compile_combatant(get_capability_definition(combatant_id)))


def build_monster_templates_from_capabilities() -> list[CombatantTemplate]:
    try:
        definitions = load_capability_definitions().values()
        monsters = [compile_combatant(item) for item in definitions if item.kind == "monster"]
        if not monsters:
            raise ValueError("Combat capability registry contains no monsters.")
        monsters = complete_monster_creature_types(monsters)
        monsters = complete_monster_end_turn_damage_auras(monsters)
        return complete_monster_trait_fingerprints(monsters)
    except Exception as exc:
        logger.exception("Failed to compile monster roster from combat capability registry.")
        raise RuntimeError("Declarative monster roster could not be created.") from exc

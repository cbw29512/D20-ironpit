from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import json
import logging
from pathlib import Path

from app.content.arena_eligibility import deferred_environment_reason
from app.content.monster_neighbor_bleed_corrections import apply_neighbor_bleed_corrections
from app.content.monster_neighbor_bleed_normalizer import normalize_neighbor_name_bleed
from app.content.monster_section_heading_corrections import apply_section_heading_corrections
from app.domain.catalog import CoverageStatus, MonsterCatalogCard
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_DATA_DIR = Path(__file__).with_name("data")
_DATA_PATH = _DATA_DIR / "srd_5_2_1_monsters.json"
_CORRECTIONS_PATH = _DATA_DIR / "srd_5_2_1_monster_corrections.json"


@lru_cache(maxsize=1)
def _canonical_monster_rows() -> tuple[dict[str, object], ...]:
    rows = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    corrections = json.loads(_CORRECTIONS_PATH.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != 328:
        raise RuntimeError("Vended parser output must contain its known 328 base records.")
    if not isinstance(corrections, list) or len(corrections) != 3:
        raise RuntimeError("SRD correction layer must contain one replacement and two restored records.")
    correction_by_id = {str(row["id"]): row for row in corrections}
    if len(correction_by_id) != 3:
        raise RuntimeError("SRD correction records must have unique ids.")
    base_ids = {str(row["id"]) for row in rows}
    replacements = [row for row in corrections if str(row["id"]) in base_ids]
    additions = [row for row in corrections if str(row["id"]) not in base_ids]
    if len(replacements) != 1 or len(additions) != 2:
        raise RuntimeError("SRD correction layer must replace one row and restore two swallowed rows.")
    combined = [correction_by_id.get(str(row["id"]), row) for row in rows] + additions
    combined = apply_neighbor_bleed_corrections(combined)
    combined = normalize_neighbor_name_bleed(combined)
    combined = apply_section_heading_corrections(combined)
    ids = {str(row["id"]) for row in combined}
    names = {str(row["name"]) for row in combined}
    if len(combined) != 330 or len(ids) != 330 or len(names) != 330:
        raise RuntimeError("SRD 5.2.1 monster catalog must contain 330 unique creatures.")
    from app.content.monster_source_integrity import validate_monster_source_integrity

    validate_monster_source_integrity(combined)
    return tuple(combined)


def load_monster_rows() -> list[dict[str, object]]:
    """Return mutation-safe copies of the once-validated canonical SRD catalog."""
    return deepcopy(list(_canonical_monster_rows()))


def _runtime_monsters_by_name() -> dict[str, CombatantTemplate]:
    try:
        from app.content.roster import build_arena_roster

        monsters = build_arena_roster().monsters
        by_name = {template.name: template for template in monsters}
        if len(by_name) != len(monsters):
            raise ValueError("Runtime monster names must be unique for automatic certification.")
        return by_name
    except Exception:
        logger.exception("Runtime monster roster failed; monster certification will fail closed.")
        return {}


def _card(row: dict[str, object], runtime: dict[str, CombatantTemplate]) -> MonsterCatalogCard:
    name = str(row["name"])
    template = runtime.get(name)
    deferred = deferred_environment_reason(name)
    if deferred:
        blockers = [f"deferred-environment:{deferred}"]
    elif template is None:
        blockers = ["monster-combat-mechanics-not-compiled"]
    else:
        try:
            from app.content.monster_source_audit import audit_monster_source

            blockers = audit_monster_source(template, row)
        except Exception:
            logger.exception("Full SRD certification failed for %s.", name)
            blockers = ["monster-source-audit-failed"]
    ready = template is not None and not blockers
    return MonsterCatalogCard(
        id=str(row["id"]), name=name, challenge_rating=str(row["challenge"]), monster_type=str(row["type"]),
        armor_class=str(row["armorClass"]), hit_points=str(row["hitPoints"]), speed=str(row["speed"]),
        source_page=int(row["sourcePage"]), source_reference=str(row["sourceReference"]),
        coverage_status=CoverageStatus.RAW_READY if ready else CoverageStatus.BLOCKED,
        runnable_template_id=template.id if ready else None,
        blockers=blockers,
    )


def build_monster_catalog() -> list[MonsterCatalogCard]:
    runtime = _runtime_monsters_by_name()
    return [_card(row, runtime) for row in load_monster_rows()]

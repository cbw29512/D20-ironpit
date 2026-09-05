from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.iron_pit_mvp_scope import affects_mvp_combat_math, feature_block
from app.content.monster_catalog import load_monster_rows
from app.content.monster_trait_source_audit import parse_trait_names
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_ARENA_NEUTRAL_BONUS_ACTIONS = frozenset({
    "Aquatic Charge", "Charge", "Cunning Action", "Leap", "Nimble Escape", "Shadow Stealth",
})


def _base_name(name: str) -> str:
    return re.sub(r"\s*\([^)]*\)$", "", name).strip()


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _base_name(name).lower()).strip("-")


def parse_bonus_action_names(source_bonus_actions: object) -> list[str]:
    return parse_trait_names(source_bonus_actions)


def bonus_action_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Block only printed Bonus Actions that change an Iron Pit MVP outcome."""
    source = row.get("bonusActions", "")
    expected = parse_bonus_action_names(source)
    issues: list[str] = []
    if template.source_bonus_action_names != expected:
        issues.append("source-bonus-action-fingerprint-mismatch")
    for name in expected:
        if _base_name(name) in _ARENA_NEUTRAL_BONUS_ACTIONS:
            continue
        block = feature_block(source, name)
        if block and not affects_mvp_combat_math(block):
            continue
        issues.append(f"uncertified-bonus-action:{_slug(name)}")
    return issues


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_bonus_action_names(name: str) -> list[str]:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return parse_bonus_action_names(row.get("bonusActions", ""))


def complete_monster_bonus_action_fingerprints(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        return [
            template.model_copy(update={"source_bonus_action_names": source_bonus_action_names(template.name)})
            if template.kind == "monster" else template
            for template in templates
        ]
    except Exception:
        logger.exception("Failed to derive canonical monster bonus-action fingerprints from SRD source.")
        raise

from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.content.monster_trait_source_audit import parse_trait_names
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_USES = re.compile(r"\bLegendary Action Uses:\s*(\d+)\.", re.I)


def parse_legendary_action_names(source_legendary_actions: object) -> list[str]:
    """Retain the printed legendary use count plus every action heading."""
    text = str(source_legendary_actions or "").strip()
    if not text:
        return []
    match = _USES.search(text)
    if not match:
        raise ValueError(f"Legendary Action Uses could not be parsed from: {text!r}")
    actions = parse_trait_names(text)
    if not actions:
        raise ValueError(f"Legendary action headings could not be parsed from: {text!r}")
    return [f"uses:{int(match.group(1))}", *actions]


def legendary_action_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Legendary off-turn action economy remains fail-closed until explicitly modeled."""
    expected = parse_legendary_action_names(row.get("legendaryActions", ""))
    issues: list[str] = []
    if template.source_legendary_action_names != expected:
        issues.append("source-legendary-action-fingerprint-mismatch")
    if expected:
        issues.append("uncertified-legendary-action-economy")
    return issues


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_legendary_action_names(name: str) -> list[str]:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return parse_legendary_action_names(row.get("legendaryActions", ""))


def complete_monster_legendary_fingerprints(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        return [
            template.model_copy(update={"source_legendary_action_names": source_legendary_action_names(template.name)})
            if template.kind == "monster" else template
            for template in templates
        ]
    except Exception:
        logger.exception("Failed to derive canonical monster legendary-action fingerprints from SRD source.")
        raise

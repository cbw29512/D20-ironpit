from __future__ import annotations

import hashlib
import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_FIELDS = ("traits", "actions", "bonusActions", "reactions")
_CASTING = re.compile(r"\bSpellcasting\b|\bcast(?:s|ing)?\b", re.IGNORECASE)


def _normalized(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def spellcasting_source_text(row: dict[str, object]) -> str:
    """Retain complete source sections that contain casting rules, not guessed spell metadata."""
    chunks: list[str] = []
    for field in _FIELDS:
        text = _normalized(row.get(field, ""))
        if text and _CASTING.search(text):
            chunks.append(f"{field}={text}")
    return "\n".join(chunks)


def spellcasting_fingerprint(row: dict[str, object]) -> str | None:
    text = spellcasting_source_text(row)
    return hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None


def spellcasting_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Fail closed until monster spell lists and concentration requirements are source-certified."""
    expected = spellcasting_fingerprint(row)
    issues: list[str] = []
    if template.source_spellcasting_fingerprint != expected:
        issues.append("source-spellcasting-fingerprint-mismatch")
    if expected is not None:
        issues.extend(("uncertified-monster-spellcasting", "spell-concentration-source-not-vendored"))
    return issues


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_spellcasting_fingerprint(name: str) -> str | None:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return spellcasting_fingerprint(row)


def complete_monster_spellcasting_fingerprints(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        return [
            template.model_copy(update={"source_spellcasting_fingerprint": source_spellcasting_fingerprint(template.name)})
            if template.kind == "monster" else template
            for template in templates
        ]
    except Exception:
        logger.exception("Failed to derive canonical monster spellcasting fingerprints from SRD source.")
        raise

from __future__ import annotations

import logging
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.content.monster_spell_selection import curated_spellcasting_issues
from app.content.monster_spell_source_parser import (
    printed_spell_names,
    source_spell_names,
    spellcasting_fingerprint,
    spellcasting_source_text,
)
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)

# Explicitly certified as irrelevant to the standard flat/open Iron Pit outcome.
# These spells are never selected as combat actions; unknown additions fail closed.
_ARENA_NEUTRAL_SPELLS = frozenset({"Detect Evil and Good", "Detect Magic", "Clairvoyance"})


def arena_neutral_spellcasting(row: dict[str, object]) -> bool:
    """True only when every source spell is explicitly certified arena-neutral."""
    spells = source_spell_names(row)
    return bool(spells) and spells <= _ARENA_NEUTRAL_SPELLS


def spellcasting_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Fail closed unless casting is neutral or covered by an explicit reviewed caster list."""
    expected = spellcasting_fingerprint(row)
    issues: list[str] = []
    if template.source_spellcasting_fingerprint != expected:
        issues.append("source-spellcasting-fingerprint-mismatch")
    if expected is None or arena_neutral_spellcasting(row):
        return issues
    curated = curated_spellcasting_issues(template, row)
    if curated is None:
        issues.extend(("uncertified-monster-spellcasting", "spell-concentration-source-not-vendored"))
    else:
        issues.extend(curated)
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

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
_SPELL_GROUP = re.compile(
    r"\b(?:At Will|\d+/Day(?: Each)?):\s*(.*?)(?=\s+(?:At Will|\d+/Day(?: Each)?):|$)",
    re.IGNORECASE,
)
# A direct cast outside the structured "casts one of the following spells" block is a
# separate combat capability until it is parsed explicitly. This keeps the neutral-spell
# audit fail-closed for bonus actions, reactions, named cast actions, and "can cast" rules.
_DIRECT_CAST = re.compile(
    r"(?:\bcasts?\s+(?!one of the following spells\b)|\bcan\s+cast\s+)",
    re.IGNORECASE,
)
# Explicitly certified as irrelevant to the standard flat/open Iron Pit outcome.
# These spells are never selected as combat actions; unknown additions fail closed.
_ARENA_NEUTRAL_SPELLS = frozenset(
    {
        "Detect Evil and Good",
        "Detect Magic",
        "Clairvoyance",
        "Minor Illusion",
        "Zone of Truth",
    }
)


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


def _printed_spell_names(row: dict[str, object]) -> set[str]:
    text = spellcasting_source_text(row)
    return {
        spell.strip()
        for group in _SPELL_GROUP.findall(text)
        for spell in group.split(",")
        if spell.strip()
    }


def arena_neutral_spellcasting(row: dict[str, object]) -> bool:
    """True only when every parsed printed spell is explicitly certified arena-neutral."""
    text = spellcasting_source_text(row)
    if _DIRECT_CAST.search(text):
        return False
    spells = _printed_spell_names(row)
    return bool(spells) and spells <= _ARENA_NEUTRAL_SPELLS


def spellcasting_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Fail closed on combat casting while allowing explicitly certified noncombat spell lists."""
    expected = spellcasting_fingerprint(row)
    issues: list[str] = []
    if template.source_spellcasting_fingerprint != expected:
        issues.append("source-spellcasting-fingerprint-mismatch")
    if expected is not None and not arena_neutral_spellcasting(row):
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
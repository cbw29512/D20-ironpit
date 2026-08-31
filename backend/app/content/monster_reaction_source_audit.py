from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_TRIGGER_RESPONSE_HEADING = re.compile(r"(?:^|(?<=\.\s))([^.]{1,80})\.\s+Trigger:\s", re.MULTILINE)
_SPELL_TRIGGER_HEADING = re.compile(
    r"(?:^|(?<=\.\s))([^.]{1,80})\.\s+"
    r"(?=[^.]{1,300}\bcasts?\b[^.]{0,200}\bin response to\b[^.]{0,100}\btrigger\b)",
    re.IGNORECASE | re.MULTILINE,
)


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _reaction_heading_matches(text: str) -> list[tuple[int, str]]:
    matches = [
        (match.start(1), match.group(1).strip())
        for pattern in (_TRIGGER_RESPONSE_HEADING, _SPELL_TRIGGER_HEADING)
        for match in pattern.finditer(text)
    ]
    return sorted(set(matches), key=lambda item: item[0])


def parse_reaction_names(source_reactions: object) -> list[str]:
    """Extract named SRD reactions from reviewed 2024 reaction prose shapes."""
    text = str(source_reactions or "").strip()
    if not text:
        return []
    names = [name for _, name in _reaction_heading_matches(text)]
    if not names:
        raise ValueError(f"SRD reaction headings could not be parsed from: {text!r}")
    return names


def reaction_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Fail closed until each printed named reaction has explicit runtime semantics."""
    expected = parse_reaction_names(row.get("reactions", ""))
    issues: list[str] = []
    if template.source_reaction_names != expected:
        issues.append("source-reaction-fingerprint-mismatch")
    issues.extend(f"uncertified-reaction:{_slug(name)}" for name in expected)
    return issues


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_reaction_names(name: str) -> list[str]:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return parse_reaction_names(row.get("reactions", ""))


def complete_monster_reaction_fingerprints(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        return [
            template.model_copy(update={"source_reaction_names": source_reaction_names(template.name)})
            if template.kind == "monster" else template
            for template in templates
        ]
    except Exception:
        logger.exception("Failed to derive canonical monster reaction fingerprints from SRD source.")
        raise

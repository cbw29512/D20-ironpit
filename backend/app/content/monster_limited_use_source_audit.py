from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_bonus_action_source_audit import arena_neutral_bonus_action
from app.content.monster_catalog import load_monster_rows
from app.content.monster_daily_use_source_audit import daily_fingerprint_implemented
from app.content.monster_reaction_source_audit import arena_neutral_reaction
from app.content.monster_recharge_source_audit import recharge_fingerprint_implemented
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_FIELDS = ("traits", "actions", "bonusActions", "reactions")
_CONNECTORS = frozenset({"a", "an", "and", "of", "or", "the", "to"})
_MARKER = re.compile(r"\((?:[^)]*(?:Recharge\s+\d(?:\s*[-–]\s*\d)?|\d+\s*/\s*Day)[^)]*)\)", re.I)
_LEGENDARY_RESISTANCE = re.compile(
    r"^traits:Legendary Resistance\s*\((?P<uses>\d+)\s*/\s*Day(?:,\s*or\s*\d+\s*/\s*Day\s+in\s+Lair)?\)$",
    re.I,
)


def _is_heading(value: str) -> bool:
    base = re.sub(r"\s*\([^)]*\)$", "", value).strip()
    words = base.split()
    if not words or len(value) > 100:
        return False
    return all(word.lower() in _CONNECTORS or re.fullmatch(r"[A-Z][A-Za-z’'\-]*", word) for word in words)


def _limited_headings(source: object) -> list[str]:
    text = re.sub(r"\s+", " ", str(source or "")).strip()
    if not text:
        return []
    names: list[str] = []
    for sentence in re.split(r"(?<=\.)\s+", text):
        candidate = sentence[:-1].strip() if sentence.endswith(".") else ""
        if candidate and _MARKER.search(candidate):
            if not _is_heading(candidate):
                raise ValueError(f"Limited-use marker is not on a parseable heading: {candidate!r}")
            names.append(candidate)
    if _MARKER.search(text) and not names:
        raise ValueError(f"SRD limited-use heading could not be parsed from: {text!r}")
    return names


def parse_limited_use_names(row: dict[str, object]) -> list[str]:
    names: list[str] = []
    for field in _FIELDS:
        names.extend(f"{field}:{name}" for name in _limited_headings(row.get(field, "")))
    return names


def _arena_neutral_limited_use(
    fingerprint: str, row: dict[str, object],
) -> bool:
    try:
        field, name = fingerprint.split(":", 1)
        if field == "actions":
            base = re.sub(r"\s*\([^)]*\)$", "", name).strip()
            source = str(row.get("actions", ""))
            requires_ambient_trees = re.search(
                rf"{re.escape(base)}(?:\s*\([^)]*\))?\.\s+"
                r"The [^.]+? (?:magically )?animates up to [^.]+? trees it can see within \d+ feet",
                source,
                re.IGNORECASE,
            )
            if requires_ambient_trees:
                return True
        if field == "bonusActions":
            return arena_neutral_bonus_action(name)
        if field == "reactions":
            return arena_neutral_reaction(name, row.get("reactions", ""))
        return False
    except Exception as exc:
        logger.exception("Failed to classify arena-neutral limited use %r.", fingerprint)
        raise RuntimeError("Limited-use arena-neutral policy could not be evaluated.") from exc


def _legendary_resistance_implemented(template: CombatantTemplate, fingerprint: str) -> bool:
    match = _LEGENDARY_RESISTANCE.fullmatch(fingerprint.strip())
    if match is None:
        return False
    uses = int(match.group("uses"))
    return any(
        item.id == "legendary-resistance" and item.max_uses == uses and item.recharge is None
        for item in template.resources
    )


def limited_use_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    expected = parse_limited_use_names(row)
    issues: list[str] = []
    if template.source_limited_use_names != expected:
        issues.append("source-limited-use-fingerprint-mismatch")
    for name in expected:
        if (
            recharge_fingerprint_implemented(template, name)
            or daily_fingerprint_implemented(template, name)
            or _legendary_resistance_implemented(template, name)
            or _arena_neutral_limited_use(name, row)
        ):
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        issues.append(f"uncertified-limited-use:{slug}")
    return issues


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_limited_use_names(name: str) -> list[str]:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return parse_limited_use_names(row)


def complete_monster_limited_use_fingerprints(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        return [
            template.model_copy(update={"source_limited_use_names": source_limited_use_names(template.name)})
            if template.kind == "monster" else template
            for template in templates
        ]
    except Exception:
        logger.exception("Failed to derive canonical monster limited-use fingerprints from SRD source.")
        raise

from __future__ import annotations

import logging

from app.content.monster_source_boundaries import (
    STRUCTURED_FIELDS,
    ends_with_heading,
    longest_terminal_monster_name,
    strip_terminal_heading,
    terminal_bare_heading,
)

logger = logging.getLogger(__name__)


def _matching_structured_fields(row: dict[str, object], heading: str) -> list[str]:
    return [
        field for field in STRUCTURED_FIELDS if ends_with_heading(row.get(field, ""), heading)
    ]


def _strip_confirmed_heading(row: dict[str, object], heading: str) -> bool:
    matching_fields = _matching_structured_fields(row, heading)
    if not matching_fields:
        return False
    row["rawText"] = strip_terminal_heading(row.get("rawText", ""), heading)
    for field in matching_fields:
        row[field] = strip_terminal_heading(row.get(field, ""), heading)
    return True


def normalize_neighbor_name_bleed(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Strip only terminal extraction headings duplicated in raw and structured SRD text."""
    try:
        monster_names = {
            str(row.get("name", "")).strip()
            for row in rows
            if str(row.get("name", "")).strip()
        }
        for row in rows:
            own_name = str(row.get("name", "")).strip()

            # Prefer a known monster name and choose the longest match so
            # "Phase Spider" cannot also be interpreted as "Spider".
            heading = longest_terminal_monster_name(
                row.get("rawText", ""),
                monster_names,
                exclude_name=own_name,
            )
            if heading is not None and _strip_confirmed_heading(row, heading):
                continue

            # Some PDF boundaries leak a section heading instead of a creature name
            # (for example "Animals" or "Bronze Dragons"). Only remove it when the
            # exact same unpunctuated title-like suffix is present in rawText and a
            # structured stat-block field.
            heading = terminal_bare_heading(row.get("rawText", ""))
            if heading is None:
                continue
            matching_fields = [
                field
                for field in STRUCTURED_FIELDS
                if terminal_bare_heading(row.get(field, "")) == heading
            ]
            if not matching_fields:
                continue
            row["rawText"] = strip_terminal_heading(row.get("rawText", ""), heading)
            for field in matching_fields:
                row[field] = strip_terminal_heading(row.get(field, ""), heading)
        return rows
    except Exception as exc:
        logger.exception("Failed to normalize terminal SRD source-boundary bleed.")
        raise RuntimeError("SRD source-boundary normalization failed.") from exc

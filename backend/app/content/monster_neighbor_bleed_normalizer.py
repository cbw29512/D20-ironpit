from __future__ import annotations

import logging

from app.content.monster_source_boundaries import (
    STRUCTURED_FIELDS,
    ends_with_heading,
    longest_terminal_monster_name,
    strip_terminal_heading,
)

logger = logging.getLogger(__name__)


def normalize_neighbor_name_bleed(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Strip terminal headings only when they exactly name another catalog monster."""
    try:
        monster_names = {
            str(row.get("name", "")).strip()
            for row in rows
            if str(row.get("name", "")).strip()
        }
        for row in rows:
            own_name = str(row.get("name", "")).strip()
            heading = longest_terminal_monster_name(
                row.get("rawText", ""),
                monster_names,
                exclude_name=own_name,
            )
            if heading is None:
                continue
            matching_fields = [
                field for field in STRUCTURED_FIELDS if ends_with_heading(row.get(field, ""), heading)
            ]
            if not matching_fields:
                continue
            row["rawText"] = strip_terminal_heading(row.get("rawText", ""), heading)
            for field in matching_fields:
                row[field] = strip_terminal_heading(row.get(field, ""), heading)
        return rows
    except Exception as exc:
        logger.exception("Failed to normalize terminal SRD neighbor-name bleed.")
        raise RuntimeError("SRD neighbor-name normalization failed.") from exc

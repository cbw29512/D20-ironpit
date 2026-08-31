from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.monster_source_boundaries import STRUCTURED_FIELDS, ends_with_heading, strip_terminal_heading

logger = logging.getLogger(__name__)
_CORRECTIONS_PATH = Path(__file__).with_name("data") / "srd_5_2_1_section_heading_corrections.json"
_EXPECTED_CORRECTIONS = 36


def apply_section_heading_corrections(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Remove only reviewed PDF section headings from exact SRD monster records."""
    try:
        specs = json.loads(_CORRECTIONS_PATH.read_text(encoding="utf-8"))
        if not isinstance(specs, list) or len(specs) != _EXPECTED_CORRECTIONS:
            raise RuntimeError(f"SRD section-heading correction layer must contain {_EXPECTED_CORRECTIONS} records.")
        by_name = {str(row.get("name", "")): row for row in rows}
        if len({str(spec.get("name", "")) for spec in specs}) != len(specs):
            raise RuntimeError("SRD section-heading corrections must target unique monster names.")

        for spec in specs:
            if not isinstance(spec, dict):
                raise RuntimeError("Each SRD section-heading correction must be an object.")
            name = str(spec.get("name", "")).strip()
            heading = str(spec.get("trailing_text", "")).strip()
            if not name or not heading:
                raise RuntimeError("SRD section-heading corrections require name and trailing_text.")
            row = by_name.get(name)
            if row is None:
                raise RuntimeError(f"SRD section-heading correction target is missing: {name}")
            if not ends_with_heading(row.get("rawText", ""), heading):
                raise RuntimeError(f"Expected {heading!r} at end of {name}.rawText; source drifted.")
            matching_fields = [
                field for field in STRUCTURED_FIELDS if ends_with_heading(row.get(field, ""), heading)
            ]
            if len(matching_fields) != 1:
                raise RuntimeError(
                    f"Expected exactly one structured field ending with {heading!r} for {name}; "
                    f"found {matching_fields!r}."
                )
            row["rawText"] = strip_terminal_heading(row.get("rawText", ""), heading)
            field = matching_fields[0]
            row[field] = strip_terminal_heading(row.get(field, ""), heading)
        return rows
    except RuntimeError:
        raise
    except Exception as exc:
        logger.exception("Failed to apply reviewed SRD section-heading corrections.")
        raise RuntimeError("SRD section-heading correction layer failed.") from exc

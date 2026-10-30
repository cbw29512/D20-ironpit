from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_REACTIVE = re.compile(
    r"Reactive\.\s+The [^.]+ can take one Reaction on every turn of combat\.",
    re.IGNORECASE,
)


def source_reaction_refresh_each_turn(source_traits: object) -> bool:
    try:
        text = str(source_traits or "")
        return _REACTIVE.search(text) is not None
    except Exception as exc:
        logger.exception("Failed to parse per-turn Reaction refresh source.")
        raise RuntimeError("Per-turn Reaction refresh source could not be parsed.") from exc


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    try:
        return {str(row["name"]): row for row in load_monster_rows()}
    except Exception:
        logger.exception("Failed to index monster rows for per-turn Reaction refresh.")
        raise


def complete_monster_reaction_refresh(
    templates: list[CombatantTemplate],
) -> list[CombatantTemplate]:
    try:
        rows = _rows_by_name()
        completed: list[CombatantTemplate] = []
        for template in templates:
            if template.kind != "monster":
                completed.append(template)
                continue
            row = rows.get(template.name)
            if row is None:
                raise ValueError(f"No SRD source row for monster {template.name!r}.")
            completed.append(template.model_copy(update={
                "reaction_refresh_each_turn": source_reaction_refresh_each_turn(
                    row.get("traits", "")
                )
            }))
        return completed
    except Exception as exc:
        logger.exception("Failed to complete per-turn Reaction refresh profiles.")
        raise RuntimeError("Per-turn Reaction refresh completion failed.") from exc


def reactive_trait_issues(
    template: CombatantTemplate,
    row: dict[str, object],
) -> tuple[list[str], bool]:
    try:
        expected = source_reaction_refresh_each_turn(row.get("traits", ""))
        if template.reaction_refresh_each_turn != expected:
            return ["reactive-source-data-mismatch"], False
        return [], expected
    except Exception as exc:
        logger.exception("Failed Reactive trait audit for %s.", template.id)
        raise RuntimeError("Reactive trait audit failed.") from exc

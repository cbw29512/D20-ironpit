from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.content.monster_save_action_source_section import save_action_source
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def _normalized(value: object) -> str:
    return re.sub(r"\s+", " ", str(value)).strip().lower()


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def _printed_save_action(action: object, row: dict[str, object]) -> bool:
    source = _normalized(save_action_source(row, action.action_cost))
    return _normalized(action.name) in source


def reconcile_monster_save_actions(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        reconciled: list[CombatantTemplate] = []
        for template in templates:
            if template.kind != "monster":
                reconciled.append(template)
                continue
            row = _rows_by_name().get(template.name)
            if row is None:
                raise ValueError(f"No SRD 5.2.1 source row for monster {template.name!r}.")
            actions = [action for action in template.saving_throw_actions if _printed_save_action(action, row)]
            reconciled.append(template.model_copy(update={"saving_throw_actions": actions}))
        return reconciled
    except Exception:
        logger.exception("Failed to reconcile compiled monster save actions to SRD headings.")
        raise

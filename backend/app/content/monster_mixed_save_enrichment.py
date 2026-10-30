from __future__ import annotations

import logging
import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_mixed_save_candidates import mixed_save_candidates
from app.domain.capabilities import CombatantDefinition

logger = logging.getLogger(__name__)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed to derive monster id for mixed-save enrichment.")
        raise RuntimeError("Monster id could not be derived.") from exc


def enrich_mixed_save_definitions(
    definitions: dict[str, CombatantDefinition],
) -> dict[str, CombatantDefinition]:
    try:
        rows = {f"srd-{_slug(str(row['name']))}": row for row in load_monster_rows()}
        enriched = dict(definitions)
        for definition_id, definition in definitions.items():
            row = rows.get(definition_id)
            if row is None or definition.kind != "monster":
                continue
            actions = list(definition.save_actions)
            known = {(item.name.lower(), item.action_cost) for item in actions}
            for field, cost in (("actions", "action"), ("bonusActions", "bonus_action")):
                for action in mixed_save_candidates(
                    definition.name, str(row.get(field, "")), cost,
                ):
                    key = (action.name.lower(), action.action_cost)
                    if key not in known:
                        actions.append(action)
                        known.add(key)
            if actions != definition.save_actions:
                enriched[definition_id] = definition.model_copy(update={"save_actions": actions})
        return enriched
    except Exception as exc:
        logger.exception("Failed mixed-save definition enrichment.")
        raise RuntimeError("Mixed-save definition enrichment failed.") from exc

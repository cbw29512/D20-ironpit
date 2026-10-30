from __future__ import annotations

import logging
import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_movement_save_candidates import movement_save_candidates
from app.domain.capabilities import CombatantDefinition

logger = logging.getLogger(__name__)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed to derive monster id for movement-save enrichment.")
        raise RuntimeError("Monster id could not be derived.") from exc


def enrich_movement_save_definitions(
    definitions: dict[str, CombatantDefinition],
) -> dict[str, CombatantDefinition]:
    """Add abstracted movement-preamble save actions after base source enrichment."""
    try:
        rows = {
            f"srd-{_slug(str(row['name']))}": row
            for row in load_monster_rows()
        }
        enriched = dict(definitions)
        for definition_id, definition in definitions.items():
            row = rows.get(definition_id)
            if row is None or definition.kind != "monster":
                continue
            actions = list(definition.save_actions)
            resources = list(definition.resources)
            known_actions = {(item.name.lower(), item.action_cost) for item in actions}
            known_resources = {item.id for item in resources}
            for field, cost in (("actions", "action"), ("bonusActions", "bonus_action")):
                parsed, parsed_resources = movement_save_candidates(
                    definition.name,
                    row.get("speed", ""),
                    str(row.get(field, "")),
                    cost,
                )
                for action in parsed:
                    if (action.name.lower(), action.action_cost) not in known_actions:
                        actions.append(action)
                        known_actions.add((action.name.lower(), action.action_cost))
                for resource in parsed_resources:
                    if resource.id not in known_resources:
                        resources.append(resource)
                        known_resources.add(resource.id)
            if actions != definition.save_actions or resources != definition.resources:
                enriched[definition_id] = definition.model_copy(update={
                    "save_actions": actions,
                    "resources": resources,
                })
        return enriched
    except Exception as exc:
        logger.exception("Failed movement-save definition enrichment.")
        raise RuntimeError("Movement-save definition enrichment failed.") from exc

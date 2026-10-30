from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def normalized_name(value: str) -> str:
    try:
        return " ".join(value.split()).strip().lower()
    except Exception as exc:
        logger.exception("Failed to normalize support-action name %r.", value)
        raise RuntimeError("Support-action name normalization failed.") from exc


def merge_support_actions(existing: list, source: list, resource_rebinds: dict[str, str]) -> list:
    try:
        known = {(normalized_name(action.name), action.action_cost) for action in existing}
        additions = []
        for action in source:
            if (normalized_name(action.name), action.action_cost) in known:
                continue
            resource_id = action.resource_id
            if resource_id is not None:
                resource_id = resource_rebinds.get(resource_id, resource_id)
            additions.append(action.model_copy(update={"resource_id": resource_id}))
        return [*existing, *additions]
    except Exception as exc:
        logger.exception("Failed to merge support actions.")
        raise RuntimeError("Support-action merge failed.") from exc

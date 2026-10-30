from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def merge_timed_self_buffs(existing: list, source: list) -> list:
    try:
        keys = {(item.name.strip().lower(), item.action_cost) for item in existing}
        additions = [
            item for item in source
            if (item.name.strip().lower(), item.action_cost) not in keys
        ]
        return [*existing, *additions]
    except Exception as exc:
        logger.exception("Failed to merge source timed self buffs.")
        raise RuntimeError("Source timed self buffs could not be enriched.") from exc


__all__ = ["merge_timed_self_buffs"]

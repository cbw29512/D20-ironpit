from __future__ import annotations

import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TargetFilter(BaseModel):
    """Source-neutral eligibility constraints for an effect target."""

    required_creature_types: list[str] = Field(default_factory=list)
    excluded_creature_types: list[str] = Field(default_factory=list)
    excluded_tags: list[str] = Field(default_factory=list)

    def allows(self, creature_type: str | None, tags: list[str]) -> bool:
        try:
            kind = (creature_type or "").lower()
            normalized_tags = {tag.lower() for tag in tags}
            required = {item.lower() for item in self.required_creature_types}
            excluded = {item.lower() for item in self.excluded_creature_types}
            excluded_tags = {item.lower() for item in self.excluded_tags}
            if required and kind not in required:
                return False
            return kind not in excluded and not (normalized_tags & excluded_tags)
        except Exception as exc:
            logger.exception("Failed to evaluate source-neutral target filter.")
            raise RuntimeError("Target filter could not be evaluated.") from exc

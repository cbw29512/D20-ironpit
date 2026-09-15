from __future__ import annotations

from pydantic import BaseModel, Field


class TargetFilter(BaseModel):
    """Source-neutral eligibility constraints for an effect target."""

    excluded_creature_types: list[str] = Field(default_factory=list)
    excluded_tags: list[str] = Field(default_factory=list)

    def allows(self, creature_type: str | None, tags: list[str]) -> bool:
        kind = (creature_type or "").lower()
        normalized_tags = {tag.lower() for tag in tags}
        return kind not in {item.lower() for item in self.excluded_creature_types} and not (
            normalized_tags & {item.lower() for item in self.excluded_tags}
        )

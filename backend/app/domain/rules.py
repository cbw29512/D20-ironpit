from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class RuleCoverageStatus(StrEnum):
    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    UNSUPPORTED = "unsupported"
    ARENA_ASSUMPTION = "arena_assumption"


class RuleCoverageEntry(BaseModel):
    id: str
    name: str
    status: RuleCoverageStatus
    notes: str
    sources: list[str] = Field(min_length=1)


class RulesCoverageReport(BaseModel):
    ruleset: str = "SRD 5.2.1 subset"
    entries: list[RuleCoverageEntry] = Field(default_factory=list)

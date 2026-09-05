from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class CoverageStatus(StrEnum):
    RAW_READY = "raw_ready"
    BLOCKED = "blocked"


class HeroCatalogCard(BaseModel):
    id: str
    name: str
    class_id: str
    class_name: str
    level: int = Field(ge=1, le=20)
    build_id: str
    build_name: str
    subclass_id: str | None = None
    subclass_name: str | None = None
    source: str
    coverage_status: CoverageStatus
    runnable_template_id: str | None = None
    blockers: list[str] = Field(default_factory=list)


class MonsterCatalogCard(BaseModel):
    id: str
    name: str
    challenge_rating: str
    monster_type: str
    size: str
    armor_class: str
    hit_points: str
    speed: str
    source_page: int = Field(ge=1)
    source_reference: str
    coverage_status: CoverageStatus
    runnable_template_id: str | None = None
    blockers: list[str] = Field(default_factory=list)


class FullContentCatalog(BaseModel):
    ruleset: str = "srd-5.2.1-2024"
    hero_count: int = Field(ge=0)
    monster_count: int = Field(ge=0)
    heroes: list[HeroCatalogCard]
    monsters: list[MonsterCatalogCard]

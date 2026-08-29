from __future__ import annotations

from app.content.audited_fighter import build_karnok_stoneward
from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.content.build_audit import assert_character_build_raw_ready
from app.domain.models import CombatantTemplate

HeroBuildKey = tuple[str, int, str]
HeroCatalogReady = tuple[str, str]


def _validated_karnok() -> tuple[HeroBuildKey, CombatantTemplate]:
    template = build_karnok_stoneward()
    profile = build_karnok_stoneward_profile()
    assert_character_build_raw_ready(profile, template)
    key: HeroBuildKey = (profile.class_id, profile.level, "great-weapon")
    return key, template


def build_certified_hero_registry() -> dict[HeroBuildKey, HeroCatalogReady]:
    key, template = _validated_karnok()
    return {key: (template.name, template.id)}


def build_certified_hero_templates() -> list[CombatantTemplate]:
    _, template = _validated_karnok()
    return [template]

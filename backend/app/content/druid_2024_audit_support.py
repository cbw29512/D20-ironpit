from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def druid_feature_audit(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    combat_relevant: bool,
    automated: bool,
    notes: str | None = None,
    runtime_attack_weapon_id: str | None = None,
) -> FeatureAudit:
    try:
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=feature_name,
            source_reference="D&D Beyond Basic Rules 2024: Druid / Character Origins",
            category=category,
            combat_relevant=combat_relevant,
            automated=automated,
            notes=notes,
            runtime_attack_weapon_id=runtime_attack_weapon_id,
        )
    except Exception:
        logger.exception("Failed to build 2024 Druid feature audit for %s.", feature_id)
        raise

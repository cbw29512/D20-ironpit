from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def monk_feature_audit(
    feature_id: str,
    name: str,
    category: str,
    *,
    combat: bool = True,
    automated: bool = True,
    weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    try:
        source = (
            "D&D SRD 5.1 (2014): Way of the Open Hand"
            if category == "subclass"
            else "D&D SRD 5.1 (2014): Monk"
        )
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=name,
            source_reference=source,
            category=category,
            combat_relevant=combat,
            automated=automated,
            runtime_attack_weapon_id=weapon_id,
            notes=notes,
        )
    except Exception:
        logger.exception("Failed to build 2014 Monk feature audit for %s.", feature_id)
        raise

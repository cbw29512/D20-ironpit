from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def life_class_feature(
    feature_id: str,
    name: str,
    *,
    combat: bool = True,
    notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=name,
        source_reference="D&D Beyond Basic Rules 2024: Cleric — Life Domain",
        category="class",
        combat_relevant=combat,
        automated=combat,
        notes=notes,
    )

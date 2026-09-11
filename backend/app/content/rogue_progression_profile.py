from __future__ import annotations

from app.content.audited_rogue_profile import build_mara_quickstep_profile
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def _audit(
    feature_id: str,
    name: str,
    category: str,
    *,
    relevant: bool,
    notes: str,
) -> FeatureAudit:
    """Build one explicit Rogue progression audit record."""
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=name,
        source_reference="D&D Beyond Basic Rules 2024: Rogue",
        category=category,
        combat_relevant=relevant,
        automated=True,
        notes=notes,
    )


def build_mara_quickstep_level2_profile() -> CharacterBuildProfile:
    """Advance Mara to level 2 while documenting Cunning Action as arena-neutral."""
    data = advance_profile_data(build_mara_quickstep_profile(), 2)
    cunning_action = _audit(
        "cunning-action",
        "Cunning Action",
        "class",
        relevant=False,
        notes=(
            "Dash, Disengage, and tactical Hide do not change the certified attack loop "
            "in the standard open Iron Pit, so the feature is retained in the audit but "
            "does not require a runtime combat binding."
        ),
    )
    data.update(
        feature_audits=[*data["feature_audits"], cunning_action.model_dump()],
        source_references=[
            *data["source_references"],
            "Basic Rules 2024: Rogue 2 — Cunning Action",
        ],
    )
    return CharacterBuildProfile.model_validate(data)

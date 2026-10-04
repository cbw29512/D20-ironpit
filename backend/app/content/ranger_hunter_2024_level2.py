from __future__ import annotations

import logging

from app.content.ranger_hunter_2024_level1 import build_ranger_2024_level1_audits
from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def build_ranger_2024_level2_audits() -> list[FeatureAudit]:
    try:
        rows = list(build_ranger_2024_level1_audits())
        rows.extend(
            [
                FeatureAudit(
                    feature_id="deft-explorer",
                    feature_name="Deft Explorer",
                    source_reference="D&D Beyond Basic Rules 2024: Ranger 2",
                    category="class",
                    combat_relevant=True,
                    automated=True,
                    notes=(
                        "Perception gains Expertise through ordinary skill-bonus math; "
                        "the two language choices are arena-neutral."
                    ),
                ),
                FeatureAudit(
                    feature_id="fighting-style",
                    feature_name="Fighting Style (Archery)",
                    source_reference="D&D Beyond Basic Rules 2024: Ranger 2",
                    category="class",
                    combat_relevant=True,
                    automated=True,
                    notes="Reuses the universal Archery ranged-weapon attack-bonus compiler.",
                ),
                FeatureAudit(
                    feature_id="longstrider",
                    feature_name="Longstrider",
                    source_reference="D&D Beyond Basic Rules 2024: Longstrider",
                    category="class",
                    combat_relevant=True,
                    automated=True,
                    notes=(
                        "Third prepared Ranger spell at level 2; reuses the already-certified explicit "
                        "2024 Longstrider speed-modifier fingerprint."
                    ),
                ),
            ]
        )
        return rows
    except Exception:
        logger.exception("Failed to compile 2024 Ranger level 2 feature audits.")
        raise

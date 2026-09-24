from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)
CLERIC = "D&D Basic Rules 2014: Cleric"
LIFE = "D&D Basic Rules 2014: Life Domain"


def _audit(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    source: str,
    automated: bool = True,
    notes: str | None = None,
) -> FeatureAudit:
    try:
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=feature_name,
            source_reference=source,
            category=category,
            combat_relevant=True,
            automated=automated,
            notes=notes,
        )
    except Exception:
        logger.exception("Failed to build high-level 2014 Life Cleric audit: %s", feature_id)
        raise


def build_high_level_cleric_life_2014_audits(level: int) -> list[FeatureAudit]:
    """Return only level-10+ Cleric/Life Domain audit deltas."""
    try:
        audits: list[FeatureAudit] = []
        if level >= 10:
            audits.append(_audit(
                "divine-intervention",
                "Divine Intervention",
                "class",
                source=CLERIC,
                notes=(
                    "Uses the universal percentile-gated healing action. On success, Iron Pit's "
                    "deterministic deity policy restores one legal living party member to effective max HP."
                ),
            ))
        if level >= 11:
            audits.append(_audit(
                "destroy-undead-2",
                "Destroy Undead (CR 2)",
                "class",
                source=CLERIC,
                notes="Uses the shared turning-save destruction threshold with CR 2 source data.",
            ))
        if level >= 12:
            audits.append(_audit("asi-12", "Ability Score Improvement", "class", source=CLERIC))
        if level >= 14:
            audits.extend([
                _audit(
                    "destroy-undead-3",
                    "Destroy Undead (CR 3)",
                    "class",
                    source=CLERIC,
                    notes="Uses the shared turning-save destruction threshold with CR 3 source data.",
                ),
                _audit(
                    "divine-strike-2d8",
                    "Divine Strike (2d8)",
                    "subclass",
                    source=LIFE,
                    notes="Scales the universal once-per-turn weapon-hit damage rider to 2d8 radiant.",
                ),
            ])
        if level >= 16:
            audits.append(_audit("asi-16", "Ability Score Improvement", "class", source=CLERIC))
        if level >= 17:
            audits.extend([
                _audit(
                    "destroy-undead-4",
                    "Destroy Undead (CR 4)",
                    "class",
                    source=CLERIC,
                    notes="Uses the shared turning-save destruction threshold with CR 4 source data.",
                ),
                _audit(
                    "supreme-healing",
                    "Supreme Healing",
                    "subclass",
                    source=LIFE,
                    notes="Uses the universal caster-owned outgoing healing-dice maximizer.",
                ),
            ])
        if level >= 18:
            audits.append(_audit("channel-divinity-3", "Channel Divinity (3/rest)", "class", source=CLERIC))
        if level >= 19:
            audits.append(_audit("asi-19", "Ability Score Improvement", "class", source=CLERIC))
        if level >= 20:
            audits.append(_audit(
                "divine-intervention-improvement",
                "Divine Intervention Improvement",
                "class",
                source=CLERIC,
                automated=False,
                notes="Requires the same universal Divine Intervention policy as level 10.",
            ))
        return audits
    except Exception:
        logger.exception("Failed high-level 2014 Life Cleric audits at level %s.", level)
        raise

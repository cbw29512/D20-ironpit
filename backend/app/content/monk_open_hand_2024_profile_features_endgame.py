from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def _feature(feature_id: str, feature_name: str, category: str, notes: str) -> FeatureAudit:
    try:
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=feature_name,
            source_reference="D&D Beyond Basic Rules 2024",
            category=category,
            combat_relevant=True,
            automated=True,
            notes=notes,
        )
    except Exception:
        logger.exception("Failed to build endgame 2024 Monk feature audit for %s.", feature_id)
        raise


def build_monk_2024_endgame_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits: list[FeatureAudit] = []
        if level >= 17:
            audits.append(_feature(
                "quivering-palm",
                "Quivering Palm",
                "subclass",
                (
                    "Reuses the universal deferred-save effect: an Unarmed Strike hit may spend 4 Focus Points "
                    "to arm one target; the vibrations can be ended harmlessly, or detonated by an Action or by "
                    "replacing one Attack-action attack. The target makes a Constitution save against the Monk DC, "
                    "taking 10d12 Force damage on failure or half on success. Same-plane and multi-day duration "
                    "qualifiers are inherently satisfied within a standard Iron Pit match."
                ),
            ))
        if level >= 18:
            audits.append(_feature(
                "superior-defense",
                "Superior Defense",
                "class",
                (
                    "Uses the universal start-turn timed self-buff path: spend 3 Focus Points at the start "
                    "of the Monk's turn for 10 rounds of resistance to every damage type except Force. "
                    "The shared source-bound lifecycle ends the effect early if the Monk is Incapacitated."
                ),
            ))
        if level >= 19:
            audits.append(_feature(
                "boon-irresistible-offense",
                "Boon of Irresistible Offense",
                "feat",
                (
                    "Raises Dexterity 20 to 21 with a maximum of 30, reuses the universal B/P/S Resistance-bypass "
                    "grant, and adds Dexterity-score damage using the attack's damage type on a natural 20."
                ),
            ))
        return audits
    except Exception:
        logger.exception("Failed to compile endgame 2024 Monk feature audits at level %s.", level)
        raise

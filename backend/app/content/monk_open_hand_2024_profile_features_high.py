from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def _feature(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    combat_relevant: bool = True,
    automated: bool = True,
    notes: str | None = None,
) -> FeatureAudit:
    try:
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=feature_name,
            source_reference="D&D Beyond Basic Rules 2024",
            category=category,
            combat_relevant=combat_relevant,
            automated=automated,
            notes=notes,
        )
    except Exception:
        logger.exception("Failed to build high-level 2024 Monk feature audit for %s.", feature_id)
        raise


def build_monk_2024_high_level_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits: list[FeatureAudit] = []
        if level >= 7:
            audits.append(
                _feature(
                    "evasion",
                    "Evasion",
                    "class",
                    notes=(
                        "Uses the shared Dexterity-save half-damage transform. "
                        "The 2024 binding disables Evasion while Incapacitated."
                    ),
                )
            )
        if level >= 8:
            audits.append(
                _feature(
                    "ability-score-improvement-l8",
                    "Ability Score Improvement (+1 Dexterity, +1 Constitution)",
                    "feat",
                    notes=(
                        "Canonical unarmed-offense progression raises Dexterity 19 to 20 and Constitution 15 to 16; "
                        "shared derived-stat logic updates AC, Initiative, attacks, Dexterity save/skills, and hit points."
                    ),
                )
            )
        if level >= 9:
            audits.append(
                _feature(
                    "acrobatic-movement",
                    "Acrobatic Movement",
                    "class",
                    combat_relevant=False,
                    automated=False,
                    notes=(
                        "RAW permits movement along vertical surfaces and across liquids while unarmored and "
                        "not wielding a Shield. The standard Iron Pit battlefield currently has no vertical-surface "
                        "or liquid-terrain state, so the feature is arena-neutral rather than approximated."
                    ),
                )
            )
        if level >= 10:
            audits.extend([
                _feature(
                    "heightened-focus",
                    "Heightened Focus",
                    "class",
                    notes=(
                        "Flurry of Blows makes three Unarmed Strikes. Focus-backed Patient Defense grants "
                        "two Martial Arts dice of Temporary HP through the shared tactical-action Temporary HP rider. "
                        "The optional Step of the Wind ally-transport choice remains deliberately unselected "
                        "by current arena automation."
                    ),
                ),
                _feature(
                    "self-restoration",
                    "Self-Restoration",
                    "class",
                    notes=(
                        "Uses the universal end-turn condition-removal primitive. "
                        "Arena priority is Charmed, then Frightened, then Poisoned when multiple eligible conditions are active."
                    ),
                ),
            ])
        if level >= 11:
            audits.append(
                _feature(
                    "fleet-step",
                    "Fleet Step",
                    "subclass",
                    notes=(
                        "Uses the universal Bonus Action follow-up tactical grant. After a different Bonus Action, "
                        "arena automation takes the resource-free Dash form of Step of the Wind immediately; "
                        "it does not invent retreat or kiting behavior."
                    ),
                )
            )
        return audits
    except Exception:
        logger.exception("Failed to compile high-level 2024 Monk feature audits at level %s.", level)
        raise

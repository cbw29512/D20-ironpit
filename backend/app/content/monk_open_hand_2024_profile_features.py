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
        logger.exception("Failed to build 2024 Monk feature audit for %s.", feature_id)
        raise


def build_monk_2024_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _feature(
                "martial-arts",
                "Martial Arts",
                "class",
                notes="Uses the shared Bonus Action attack grant; no Attack action prerequisite is imposed.",
            ),
            _feature("unarmored-defense", "Unarmored Defense", "class"),
        ]
        if level >= 2:
            audits.extend([
                _feature(
                    "monks-focus",
                    "Monk's Focus",
                    "class",
                    notes="Focus Points fuel shared Flurry, Patient Defense, and Step of the Wind mechanics.",
                ),
                _feature(
                    "unarmored-movement",
                    "Unarmored Movement",
                    "class",
                    notes=(
                        f"Adds {15 if level >= 6 else 10} feet to Speed while unarmored and not wielding a Shield."
                    ),
                ),
                _feature(
                    "uncanny-metabolism",
                    "Uncanny Metabolism",
                    "class",
                    notes="On Initiative, once per Long Rest, restores Focus and heals Monk level + one Martial Arts die.",
                ),
            ])
        if level >= 3:
            audits.extend([
                _feature(
                    "deflect-attacks",
                    "Deflect Attacks",
                    "class",
                    notes="Uses universal Reaction damage reduction for qualifying B/P/S attack damage.",
                ),
                _feature(
                    "open-hand-technique",
                    "Open Hand Technique",
                    "subclass",
                    notes="Arena automation selects Topple on Flurry hits using the shared Dexterity-save-to-Prone rider.",
                ),
            ])
        if level >= 4:
            audits.extend([
                _feature(
                    "ability-score-improvement-l4",
                    "Ability Score Improvement (+2 Dexterity)",
                    "feat",
                    notes=(
                        "Canonical unarmed-offense progression raises Dexterity 17 to 19; shared derived-stat "
                        "logic updates AC, Initiative, attacks, Dexterity save, and Dexterity skills."
                    ),
                ),
                _feature(
                    "slow-fall",
                    "Slow Fall",
                    "class",
                    combat_relevant=False,
                    automated=False,
                    notes="The standard Iron Pit arena has no falling hazard; source behavior is preserved without a combat resolver.",
                ),
            ])
        if level >= 5:
            audits.extend([
                _feature(
                    "extra-attack",
                    "Extra Attack",
                    "class",
                    notes="Uses the shared two-slot Attack action; no Monk-specific attack resolver is added.",
                ),
                _feature(
                    "stunning-strike",
                    "Stunning Strike",
                    "class",
                    notes=(
                        "Uses the universal resource-backed once-per-turn on-hit save rider. "
                        "Failure applies Stunned until the start of Kael's next turn; success halves Speed "
                        "and grants Advantage on the next attack against the target before then."
                    ),
                ),
            ])
        if level >= 6:
            audits.extend([
                _feature(
                    "empowered-strikes",
                    "Empowered Strikes",
                    "class",
                    notes="Uses the universal attack damage-type choice primitive: Force or the strike's normal damage type.",
                ),
                _feature(
                    "wholeness-of-body",
                    "Wholeness of Body",
                    "subclass",
                    notes="Uses the shared limited-use Bonus Action self-healing action with the Martial Arts die.",
                ),
            ])
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
        audits.extend([
            _feature(
                "alert",
                "Alert",
                "feat",
                notes="Adds Proficiency Bonus to Initiative; arena policy declines the optional ally initiative swap.",
            ),
            _feature(
                "resourceful",
                "Resourceful",
                "species",
                notes="Fresh-rest arena initialization starts Kael with Heroic Inspiration.",
            ),
            _feature("skillful", "Skillful", "species", combat_relevant=False, notes="Perception proficiency selected."),
            _feature(
                "versatile",
                "Versatile",
                "species",
                combat_relevant=False,
                notes="Recommended Skilled Origin feat selected.",
            ),
            _feature(
                "skilled",
                "Skilled",
                "feat",
                combat_relevant=False,
                notes="History, Nature, and Religion proficiencies selected.",
            ),
            _feature("unarmed-strike", "Unarmed Strike", "equipment"),
        ])
        return audits
    except Exception:
        logger.exception("Failed to compile 2024 Monk feature audits at level %s.", level)
        raise

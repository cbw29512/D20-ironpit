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


def build_druid_2024_progression_audits(level: int) -> list[FeatureAudit]:
    """Return level-gated Druid progression audits from level 4 onward."""
    try:
        audits: list[FeatureAudit] = []
        if level >= 4:
            audits.append(druid_feature_audit(
                "ability-score-improvement-l4", "Ability Score Improvement (+2 Wisdom)", "class",
                combat_relevant=True, automated=True,
                notes="Canonical land-damage progression raises Wisdom 17→19 and all derived Druid spell math.",
            ))
        if level >= 5:
            audits.append(druid_feature_audit(
                "wild-resurgence", "Wild Resurgence", "class", combat_relevant=True, automated=True,
                notes=(
                    "Universal resource conversion: at zero Wild Shape, spend one spell slot with no "
                    "action to regain one use, limited once on each turn; alternatively spend one "
                    "Wild Shape plus the once-per-Long-Rest gate to regain one level 1 spell slot."
                ),
            ))
        if level >= 6:
            audits.append(druid_feature_audit(
                "natural-recovery", "Natural Recovery", "subclass", combat_relevant=True, automated=True,
                notes=(
                    "Once per Long Rest, cast one prepared level 1+ Circle Spell without expending "
                    "a spell slot via the universal alternate-spell-cast grant. The Short-Rest slot "
                    "recovery half occurs outside an active Iron Pit match and needs no fight-time resolver."
                ),
            ))
        if level >= 7:
            audits.append(druid_feature_audit(
                "elemental-fury-potent-spellcasting", "Elemental Fury: Potent Spellcasting", "class",
                combat_relevant=True, automated=True,
                notes=(
                    "Canonical Elemental Fury choice adds Wisdom modifier to every damaging Druid "
                    "cantrip through the generic spell-action damage bonus."
                ),
            ))
        if level >= 8:
            audits.extend([
                druid_feature_audit(
                    "ability-score-improvement-l8", "Ability Score Improvement (+1 Wisdom, +1 Charisma)",
                    "class", combat_relevant=True, automated=True,
                    notes="Canonical land-damage progression raises Wisdom 19→20 and Charisma 15→16.",
                ),
                druid_feature_audit(
                    "wild-shape-improvement-l8", "Wild Shape Improvement", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Known forms increase to eight, CR 1 and Fly Speed become legal; "
                        "canonical combat form is Brown Bear."
                    ),
                ),
            ])
        if level >= 9:
            audits.extend([
                druid_feature_audit(
                    "druid-combat-spells-5", "Level 5 Spellcasting", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Canonical combat-first preparation adds 2024 Thunderwave and Mass Cure Wounds. "
                        "Thunderwave reuses universal failed-save forced movement; Mass Cure Wounds reuses "
                        "the shared multi-target healing action."
                    ),
                ),
                druid_feature_audit(
                    "circle-spells-5-wall-of-stone", "Circle Spells: Arid — Wall of Stone", "subclass",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Required level-9 Arid Circle Spell uses the universal persistent-barrier engine: "
                        "exact ten-panel geometry, stone support, movement and line-of-effect blocking, "
                        "AC/HP/immunities, destruction breaches, Concentration cleanup, full-duration "
                        "permanence, spell-slot casting, and Natural Recovery alternate casting."
                    ),
                ),
            ])
        return audits
    except Exception:
        logger.exception("Failed to build 2024 Druid progression audits for level %s.", level)
        raise

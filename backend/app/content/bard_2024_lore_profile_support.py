from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def lore_bard_level3_audits() -> list[FeatureAudit]:
    return [
        FeatureAudit(
            feature_id="lore-bonus-proficiencies",
            feature_name="Bonus Proficiencies",
            source_reference="D&D Beyond Basic Rules 2024: College of Lore 3",
            category="subclass",
            combat_relevant=False,
            automated=False,
            notes="Canonical choices are Arcana, Deception, and Sleight of Hand; no arena mechanic changes.",
        ),
        FeatureAudit(
            feature_id="cutting-words",
            feature_name="Cutting Words",
            source_reference="D&D Beyond Basic Rules 2024: College of Lore 3",
            category="subclass",
            combat_relevant=True,
            automated=True,
            notes="Uses the universal reaction roll-penalty capability with 2024 sight-only legality.",
        ),
        FeatureAudit(
            feature_id="bard-combat-spells-2",
            feature_name="Level 2 Bard Combat Spells",
            source_reference="D&D Beyond Basic Rules 2024: Bard 3",
            category="class",
            combat_relevant=True,
            automated=True,
            notes="Shatter is the canonical level-2 damage spell.",
        ),
    ]



def bard_level4_asi_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="ability-score-improvement-4",
        feature_name="Ability Score Improvement",
        source_reference="D&D Beyond Basic Rules 2024: Bard 4",
        category="class",
        combat_relevant=True,
        automated=True,
        notes="+2 Charisma is applied to Lyra's persistent progression.",
    )


def bard_level5_font_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="font-of-inspiration",
        feature_name="Font of Inspiration",
        source_reference="D&D Beyond Basic Rules 2024: Bard 5",
        category="class",
        combat_relevant=True,
        automated=True,
        notes=(
            "Short/Long Rest recovery is outside a match because Iron Pit resets between matches; "
            "spell-slot conversion uses the universal resource-conversion schema."
        ),
    )


def bard_level6_magical_discoveries_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="magical-discoveries",
        feature_name="Magical Discoveries",
        source_reference="D&D Beyond Basic Rules 2024: College of Lore 6",
        category="subclass",
        combat_relevant=True,
        automated=True,
        notes=(
            "Canonical always-prepared choices are Bless and Guiding Bolt. "
            "Both bind existing 2024 spell primitives; no new combat resolver is introduced."
        ),
    )


def bard_level7_countercharm_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="countercharm",
        feature_name="Countercharm",
        source_reference="D&D Beyond Basic Rules 2024: Bard 7",
        category="class",
        combat_relevant=True,
        automated=True,
        notes=(
            "Uses the universal failed-save reroll primitive: Reaction, self or ally within 30 feet, "
            "only against effects applying Charmed or Frightened, replacement save with Advantage."
        ),
    )


def bard_level8_asi_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="ability-score-improvement-8",
        feature_name="Ability Score Improvement",
        source_reference="D&D Beyond Basic Rules 2024: Bard 8",
        category="class",
        combat_relevant=True,
        automated=True,
        notes="+1 Charisma and +1 Wisdom, producing Charisma 20 and Wisdom 16.",
    )

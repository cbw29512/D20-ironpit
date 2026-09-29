from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def bard_level13_spells_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="bard-combat-spells-7",
        feature_name="Level 7 Bard Spells",
        source_reference="D&D Beyond Basic Rules 2024: Bard 13; Spells — Finger of Death",
        category="class",
        combat_relevant=True,
        automated=True,
        notes=(
            "Finger of Death is prepared through Magical Secrets and reuses the universal "
            "save-damage primitive. Its Zombie creation rider is arena-inert because summoning "
            "is disabled by Iron Pit contract."
        ),
    )


def bard_level14_peerless_skill_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="peerless-skill",
        feature_name="Peerless Skill",
        source_reference="D&D Beyond Basic Rules 2024: College of Lore 14",
        category="subclass",
        combat_relevant=True,
        automated=True,
        notes=(
            "Uses the universal resource-backed failed-d20 bonus die for self attack rolls "
            "and ability checks. Bardic Inspiration is consumed only when the revised test succeeds."
        ),
    )


def bard_level15_spells_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="bard-combat-spells-8",
        feature_name="Level 8 Bard Spells",
        source_reference="D&D Beyond Basic Rules 2024: Bard 15; Spells — Sunburst",
        category="class",
        combat_relevant=True,
        automated=True,
        notes=(
            "Sunburst is prepared through Magical Secrets and composes the existing area save-damage "
            "and failed-save timed-condition primitives: Constitution save, 12d6 Radiant, half on success, "
            "Blinded for up to 1 minute on failure with an end-of-turn repeat save."
        ),
    )


def bard_level16_asi_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="ability-score-improvement-16",
        feature_name="Ability Score Improvement",
        source_reference="D&D Beyond Basic Rules 2024: Bard 16",
        category="class",
        combat_relevant=True,
        automated=True,
        notes="+2 Wisdom is applied to Lyra's persistent progression, producing Wisdom 20.",
    )


def bard_level17_spells_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="bard-combat-spells-9",
        feature_name="Level 9 Bard Spells",
        source_reference="D&D Beyond Basic Rules 2024: Bard 17; Spells — Power Word Kill",
        category="class",
        combat_relevant=True,
        automated=True,
        notes=(
            "2024 Power Word Kill reuses the universal HP-threshold instant-death action "
            "with a typed fallback-damage payload: a target at 100 HP or fewer dies; "
            "otherwise it takes 12d12 Psychic damage through normal damage defenses."
        ),
    )


def bard_level18_superior_inspiration_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="superior-inspiration",
        feature_name="Superior Inspiration",
        source_reference="D&D Beyond Basic Rules 2024: Bard 18",
        category="class",
        combat_relevant=True,
        automated=True,
        notes=(
            "On Initiative, if Bardic Inspiration has fewer than two uses remaining, "
            "the universal initiative-refill primitive restores it to two."
        ),
    )


def bard_level19_boon_of_fate_audit() -> FeatureAudit:
    return FeatureAudit(
        feature_id="boon-of-fate",
        feature_name="Boon of Fate",
        source_reference="D&D Beyond Basic Rules 2024: Bard 19; Epic Boon — Boon of Fate",
        category="feat",
        combat_relevant=True,
        automated=True,
        notes=(
            "Lyra legally chooses Boon of Fate instead of the recommended Boon of Spell Recall. "
            "The feat applies +1 Intelligence and reuses the already-certified universal "
            "resource-backed 2d4 D20 outcome-adjustment primitive within 60 feet."
        ),
    )

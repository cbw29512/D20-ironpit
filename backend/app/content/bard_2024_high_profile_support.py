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

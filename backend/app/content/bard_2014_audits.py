from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def build_bard_2014_feature_audits(level: int) -> list[FeatureAudit]:
    if level not in range(1, 21):
        raise ValueError("2014 Bard feature audit covers levels 1 through 20.")
    rows = [
        FeatureAudit(
            feature_id="half-elf", feature_name="Half-Elf",
            source_reference="D&D Basic Rules 2014: Half-Elf",
            category="species", combat_relevant=False, automated=True,
        ),
        FeatureAudit(
            feature_id="rapier", feature_name="Rapier",
            source_reference="D&D Basic Rules 2014: Equipment",
            category="equipment", combat_relevant=True, automated=True,
            runtime_attack_weapon_id="rapier",
        ),
        FeatureAudit(
            feature_id="bardic-inspiration", feature_name="Bardic Inspiration",
            source_reference="D&D Basic Rules 2014: Bard 1",
            category="class", combat_relevant=True, automated=True,
        ),
        FeatureAudit(
            feature_id="spellcasting", feature_name="Spellcasting",
            source_reference="D&D Basic Rules 2014: Bard 1",
            category="class", combat_relevant=True, automated=True,
        ),
    ]
    if level >= 2:
        rows += [
            FeatureAudit(
                feature_id="jack-of-all-trades", feature_name="Jack of All Trades",
                source_reference="D&D Basic Rules 2014: Bard 2",
                category="class", combat_relevant=True, automated=True,
                notes="Initiative includes half proficiency because it is an unproficient Dexterity ability check.",
            ),
            FeatureAudit(
                feature_id="song-of-rest", feature_name="Song of Rest",
                source_reference="D&D Basic Rules 2014: Bard 2",
                category="class", combat_relevant=False, automated=True,
            ),
        ]
    if level >= 3:
        rows.append(FeatureAudit(
            feature_id="college-lore", feature_name="College of Lore",
            source_reference="D&D Basic Rules 2014: College of Lore",
            category="subclass", combat_relevant=False, automated=True,
        ))
    return rows

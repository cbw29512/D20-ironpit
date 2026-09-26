from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def build_sorcerer_draconic_2014_high_level_audits(level: int) -> list[FeatureAudit]:
    rows: list[FeatureAudit] = []
    if level >= 10:
        rows += [
            FeatureAudit(
                feature_id="distant-spell",
                feature_name="Metamagic: Distant Spell",
                source_reference="D&D Basic Rules 2014: Sorcerer 3, Metamagic",
                category="class", combat_relevant=True, automated=True,
                notes=(
                    "Selected as Nyra's third Metamagic option. The shared resource-backed spell-range "
                    "modifier doubles qualifying spell range and spends 1 Sorcery Point only when extended "
                    "range is actually required, with Python/browser parity."
                ),
            ),
            FeatureAudit(
                feature_id="teleportation-circle",
                feature_name="Teleportation Circle",
                source_reference="D&D Basic Rules 2014: Teleportation Circle",
                category="class", combat_relevant=False, automated=True,
                notes="Legal Sorcerer choice; one-minute casting time and travel purpose are arena-neutral.",
            ),
        ]
    if level >= 11:
        rows.append(FeatureAudit(
            feature_id="move-earth", feature_name="Move Earth",
            source_reference="D&D Basic Rules 2014: Move Earth",
            category="class", combat_relevant=False, automated=True,
            notes="Legal sixth-level Sorcerer choice recorded as arena-neutral for Iron Pit combat.",
        ))
    if level >= 12:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-12",
            feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Sorcerer 12",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "+2 Constitution raises Nyra from 12 to 14 and shared character math updates Constitution "
                "saves plus retroactive hit points."
            ),
        ))
    if level >= 13:
        rows.append(FeatureAudit(
            feature_id="teleport", feature_name="Teleport",
            source_reference="D&D Basic Rules 2014: Teleport",
            category="class", combat_relevant=False, automated=True,
            notes="Legal seventh-level Sorcerer choice recorded as arena-neutral for Iron Pit combat.",
        ))
    if level >= 14:
        rows.append(FeatureAudit(
            feature_id="dragon-wings", feature_name="Dragon Wings",
            source_reference="D&D Basic Rules 2014: Draconic Bloodline 14",
            category="subclass", combat_relevant=True, automated=True,
            notes=(
                "Permanent 30-foot flying speed binds directly to the universal movement fingerprint; "
                "no source-name-specific movement resolver is used."
            ),
        ))
    if level >= 15:
        rows.append(FeatureAudit(
            feature_id="tongues", feature_name="Tongues",
            source_reference="D&D Basic Rules 2014: Tongues",
            category="class", combat_relevant=False, automated=True,
            notes="Legal additional Sorcerer spell known; language comprehension is arena-neutral.",
        ))
    if level >= 16:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-16",
            feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Sorcerer 16",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "+2 Constitution raises Nyra from 14 to 16; shared derived-stat math updates Constitution "
                "saves and retroactive hit points."
            ),
        ))
    return rows

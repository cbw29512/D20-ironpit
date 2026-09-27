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
                feature_id="creation",
                feature_name="Creation",
                source_reference="D&D Basic Rules 2014: Creation",
                category="class", combat_relevant=False, automated=True,
                notes="Legal fifth-level Sorcerer choice recorded as arena-neutral for Iron Pit combat.",
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
                "Bonus Action manifestation binds to the universal persistent movement-mode grant. "
                "While active, Fly speed equals current Speed; fresh combat state resets the grant."
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
    if level >= 17:
        rows += [
            FeatureAudit(
                feature_id="extended-spell",
                feature_name="Metamagic: Extended Spell",
                source_reference="D&D Basic Rules 2014: Sorcerer 3, Metamagic",
                category="class", combat_relevant=True, automated=True,
                notes=(
                    "Selected as Nyra's fourth Metamagic option. The universal resource-backed duration "
                    "modifier spends 1 Sorcery Point and doubles a qualifying spell's duration up to 24 hours "
                    "with Python/browser parity."
                ),
            ),
            FeatureAudit(
                feature_id="water-breathing",
                feature_name="Water Breathing",
                source_reference="D&D Basic Rules 2014: Water Breathing",
                category="class", combat_relevant=False, automated=True,
                notes="Legal additional Sorcerer spell known; underwater breathing is arena-neutral.",
            ),
        ]
    if level >= 18:
        rows.append(FeatureAudit(
            feature_id="draconic-presence",
            feature_name="Draconic Presence",
            source_reference="D&D Basic Rules 2014: Draconic Bloodline 18",
            category="subclass", combat_relevant=True, automated=True,
            notes=(
                "Fear mode binds to the universal source-owned hostile start-turn aura: 60-foot radius, "
                "5 Sorcery Points, concentration, Wisdom save, Frightened on failure, and source-specific "
                "24-hour success immunity."
            ),
        ))
    if level >= 19:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-19",
            feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Sorcerer 19",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "+2 Dexterity raises Nyra from 13 to 15; shared derived-stat math updates AC, initiative, "
                "Dexterity skills, attacks, and saving throws where applicable."
            ),
        ))
    if level >= 20:
        rows.append(FeatureAudit(
            feature_id="sorcerous-restoration",
            feature_name="Sorcerous Restoration",
            source_reference="D&D Basic Rules 2014: Sorcerer 20",
            category="class", combat_relevant=False, automated=True,
            notes=(
                "RAW recovery occurs when finishing a short rest. Iron Pit has no in-fight short-rest phase "
                "and resets combatants between matches, so no combat resolver is required."
            ),
        ))
    return rows

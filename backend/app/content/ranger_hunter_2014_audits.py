from __future__ import annotations

from app.content.ranger_hunter_2014_high_audits import build_ranger_hunter_2014_high_feature_audits
from app.domain.character_builds import FeatureAudit


def build_ranger_hunter_2014_feature_audits(level: int) -> list[FeatureAudit]:
    rows = [
        FeatureAudit(
            feature_id="wood-elf", feature_name="Wood Elf",
            source_reference="D&D Basic Rules 2014: Wood Elf",
            category="species", combat_relevant=True, automated=True,
            notes="DEX +2, WIS +1, 35-foot speed, Keen Senses, and Fey Ancestry reuse shared character/save mechanics.",
        ),
        FeatureAudit(
            feature_id="longbow", feature_name="Longbow",
            source_reference="D&D Basic Rules 2014: Equipment",
            category="equipment", combat_relevant=True, automated=True,
            runtime_attack_weapon_id="longbow",
        ),
        FeatureAudit(
            feature_id="shortsword", feature_name="Shortsword",
            source_reference="D&D Basic Rules 2014: Equipment",
            category="equipment", combat_relevant=True, automated=True,
            runtime_attack_weapon_id="shortsword",
        ),
        FeatureAudit(
            feature_id="favored-enemy", feature_name="Favored Enemy",
            source_reference="D&D Basic Rules 2014: Ranger 1",
            category="class", combat_relevant=False, automated=True,
            notes=(
                "Canonical favored enemy: monstrosities. Tracking and information-recall benefits are arena-neutral "
                "until Foe Slayer uses the stored creature-type choice at level 20."
            ),
        ),
        FeatureAudit(
            feature_id="natural-explorer", feature_name="Natural Explorer",
            source_reference="D&D Basic Rules 2014: Ranger 1",
            category="class", combat_relevant=False, automated=True,
            notes="Travel and exploration benefits are outside an in-progress Iron Pit fight.",
        ),
    ]
    if level >= 2:
        rows += [
            FeatureAudit(
                feature_id="fighting-style", feature_name="Fighting Style (Archery)",
                source_reference="D&D Basic Rules 2014: Ranger 2",
                category="class", combat_relevant=True, automated=True,
                notes="Reuses the universal Archery ranged-weapon attack-bonus compiler.",
            ),
            FeatureAudit(
                feature_id="spellcasting", feature_name="Spellcasting",
                source_reference="D&D Basic Rules 2014: Ranger 2",
                category="class", combat_relevant=True, automated=True,
                notes="Known-spell count, slots, healing, and buffs use shared 2014 spell primitives.",
            ),
        ]
    if level >= 3:
        rows += [
            FeatureAudit(
                feature_id="colossus-slayer", feature_name="Colossus Slayer",
                source_reference="D&D Basic Rules 2014: Hunter 3",
                category="subclass", combat_relevant=True, automated=True,
                notes=(
                    "Uses the shared once-per-turn weapon-hit damage rider with a target-below-max-HP "
                    "qualification and weapon damage-type inheritance."
                ),
            ),
            FeatureAudit(
                feature_id="primeval-awareness", feature_name="Primeval Awareness",
                source_reference="D&D Basic Rules 2014: Ranger 3",
                category="class", combat_relevant=False, automated=True,
                notes="Presence sensing reveals neither location nor number and does not alter standard arena combat.",
            ),
        ]
    if level >= 4:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-4", feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Ranger 4",
            category="class", combat_relevant=True, automated=True,
            notes="Canonical archer progression raises Dexterity from 17 to 19 and recomputes derived combat values.",
        ))
    if level >= 5:
        rows.append(FeatureAudit(
            feature_id="extra-attack", feature_name="Extra Attack",
            source_reference="D&D Basic Rules 2014: Ranger 5",
            category="class", combat_relevant=True, automated=True,
            notes="Uses the universal Attack action with two weapon-attack slots.",
        ))
    if level >= 6:
        rows += [
            FeatureAudit(
                feature_id="favored-enemy-improvement-6", feature_name="Favored Enemy Improvement",
                source_reference="D&D Basic Rules 2014: Ranger 6",
                category="class", combat_relevant=False, automated=True,
                notes=(
                    "Canonical additional favored enemy: undead. Tracking/recall remains arena-neutral "
                    "until Foe Slayer uses the stored creature-type choice at level 20."
                ),
            ),
            FeatureAudit(
                feature_id="natural-explorer-improvement-6", feature_name="Natural Explorer Improvement",
                source_reference="D&D Basic Rules 2014: Ranger 6",
                category="class", combat_relevant=False, automated=True,
                notes="Adds another favored terrain; overland travel remains outside an in-progress fight.",
            ),
        ]
    if level >= 7:
        rows.append(FeatureAudit(
            feature_id="steel-will", feature_name="Defensive Tactics (Steel Will)",
            source_reference="D&D Basic Rules 2014: Hunter 7",
            category="subclass", combat_relevant=True, automated=True,
            notes="Reuses universal saving-throw Advantage tagged to frightened effects.",
        ))
    if level >= 8:
        rows += [
            FeatureAudit(
                feature_id="ability-score-improvement-8", feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Ranger 8",
                category="class", combat_relevant=True, automated=True,
                notes="Raises Dexterity 19 to 20 and Wisdom 14 to 15; shared math recomputes derived values.",
            ),
            FeatureAudit(
                feature_id="lands-stride", feature_name="Land's Stride",
                source_reference="D&D Basic Rules 2014: Ranger 8",
                category="class", combat_relevant=True, automated=True,
                notes="Reuses the same shared 2014 Land's Stride binding as Circle of the Land Druid.",
            ),
        ]
    rows.extend(build_ranger_hunter_2014_high_feature_audits(level))
    return rows

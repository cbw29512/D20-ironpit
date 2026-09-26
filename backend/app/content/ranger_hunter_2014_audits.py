from __future__ import annotations

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
            notes="Tracking and information-recall benefits do not alter standard Iron Pit combat at level 1.",
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
                notes="Adds another favored enemy/language choice; tracking/recall remains arena-neutral.",
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
    if level >= 10:
        rows += [
            FeatureAudit(
                feature_id="natural-explorer-improvement-10", feature_name="Natural Explorer Improvement",
                source_reference="D&D Basic Rules 2014: Ranger 10",
                category="class", combat_relevant=False, automated=True,
                notes="Adds another favored terrain; overland travel remains outside an in-progress fight.",
            ),
            FeatureAudit(
                feature_id="hide-in-plain-sight", feature_name="Hide in Plain Sight",
                source_reference="D&D Basic Rules 2014: Ranger 10",
                category="class", combat_relevant=False, automated=False,
                notes=(
                    "Requires one minute of camouflage preparation using natural materials and a qualifying "
                    "solid surface; the default open Pit supplies neither requirement."
                ),
            ),
        ]
    if level >= 11:
        rows.append(FeatureAudit(
            feature_id="volley", feature_name="Multiattack (Volley)",
            source_reference="D&D Basic Rules 2014: Hunter 11",
            category="subclass", combat_relevant=True, automated=True,
            notes=(
                "Uses the universal area-weapon-attack action: choose a point in weapon range, "
                "find opposing creatures within 10 feet, then resolve one normal longbow attack per target."
            ),
        ))
    if level >= 12:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-12", feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Ranger 12",
            category="class", combat_relevant=True, automated=True,
            notes="Canonical archer progression raises Wisdom from 15 to 17; shared math recomputes Wisdom-derived values.",
        ))
    if level >= 14:
        rows += [
            FeatureAudit(
                feature_id="favored-enemy-improvement-14", feature_name="Favored Enemy Improvement",
                source_reference="D&D Basic Rules 2014: Ranger 14",
                category="class", combat_relevant=False, automated=True,
                notes="Adds another favored enemy/language choice; tracking and recall remain arena-neutral.",
            ),
            FeatureAudit(
                feature_id="vanish", feature_name="Vanish",
                source_reference="D&D Basic Rules 2014: Ranger 14",
                category="class", combat_relevant=False, automated=False,
                notes=(
                    "Bonus Action Hide has no automatic legal Hide position in the standard Iron Pit arena, "
                    "and the nonmagical tracking protection is noncombat. No Ranger-specific stealth resolver is created."
                ),
            ),
        ]
    if level >= 15:
        rows.append(FeatureAudit(
            feature_id="superior-hunters-defense-evasion",
            feature_name="Superior Hunter's Defense (Evasion)",
            source_reference="D&D Basic Rules 2014: Hunter 15",
            category="subclass", combat_relevant=True, automated=True,
            notes="Canonical Hunter choice reuses the universal Evasion save-damage primitive already used by Rogue.",
        ))
    if level >= 16:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-16", feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Ranger 16",
            category="class", combat_relevant=True, automated=True,
            notes="Canonical archer progression raises Wisdom from 17 to 19; shared math recomputes Wisdom-derived values.",
        ))
    if level >= 17:
        rows.append(FeatureAudit(
            feature_id="spellcasting-5th-level", feature_name="Spellcasting (5th-level spells)",
            source_reference="D&D Basic Rules 2014: Ranger 17",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "Unlocks one 5th-level spell slot and the tenth known Ranger spell. "
                "The canonical known spell is Commune with Nature, retained as arena-out-of-scope utility."
            ),
        ))
    if level >= 18:
        rows.append(FeatureAudit(
            feature_id="feral-senses", feature_name="Feral Senses",
            source_reference="D&D Basic Rules 2014: Ranger 18",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "Reuses a universal visibility-derived attack-modifier suppression: inability to see the target "
                "no longer adds attack Disadvantage. It does not grant actual sight or suppress unrelated Disadvantage."
            ),
        ))
    return rows

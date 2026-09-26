from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def build_ranger_hunter_2014_high_feature_audits(level: int) -> list[FeatureAudit]:
    rows: list[FeatureAudit] = []
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
                notes=(
                    "Canonical additional favored enemy: fiends. Tracking and recall remain arena-neutral "
                    "until Foe Slayer uses the stored creature-type choice at level 20."
                ),
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
    if level >= 19:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-19", feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Ranger 19",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "Canonical archer progression raises Wisdom 19 to 20 and Constitution 14 to 15. "
                "The Wisdom increase improves Ranger spellcasting and the level-20 Foe Slayer modifier."
            ),
        ))
    if level >= 20:
        rows.append(FeatureAudit(
            feature_id="foe-slayer", feature_name="Foe Slayer",
            source_reference="D&D Basic Rules 2014: Ranger 20",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "Uses the RAW damage-roll option deterministically on the first successful weapon hit each turn "
                "against Rowan's favored enemy types (monstrosity, undead, fiend). Reuses the generic "
                "once-per-turn hit rider with a flat Wisdom modifier and creature-type qualification."
            ),
        ))
    return rows

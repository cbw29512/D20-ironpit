from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def build_varek_fiend_2014_low_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            FeatureAudit(
                feature_id="human", feature_name="Human",
                source_reference="D&D Basic Rules 2014: Human",
                category="species", combat_relevant=True, automated=True,
                notes="The 2014 Human +1 increase to every ability score is represented directly in the certified build profile.",
            ),
            FeatureAudit(
                feature_id="light-crossbow", feature_name="Light Crossbow",
                source_reference="D&D Basic Rules 2014: Equipment",
                category="equipment", combat_relevant=True, automated=True,
                runtime_attack_weapon_id="light-crossbow",
                notes="The starting light crossbow uses the shared ranged weapon attack resolver and remains the certified mundane fallback.",
            ),
            FeatureAudit(
                feature_id="pact-magic", feature_name="Pact Magic",
                source_reference="D&D Basic Rules 2014: Warlock 1",
                category="class", combat_relevant=True, automated=True,
                notes="Pact Magic uses the shared spell-slot resource model.",
            ),
            FeatureAudit(
                feature_id="fiend-patron", feature_name="The Fiend",
                source_reference="D&D Basic Rules 2014: Otherworldly Patron — The Fiend",
                category="subclass", combat_relevant=True, automated=True,
                notes="2014 patron begins at level 1; its expanded list adds choices rather than automatic known spells.",
            ),
            FeatureAudit(
                feature_id="dark-ones-blessing", feature_name="Dark One's Blessing",
                source_reference="D&D Basic Rules 2014: The Fiend 1",
                category="subclass", combat_relevant=True, automated=True,
                notes="Uses the universal hostile-zeroing trigger and Temporary HP primitive.",
            ),
            FeatureAudit(
                feature_id="eldritch-blast", feature_name="Eldritch Blast",
                source_reference="D&D Basic Rules 2014: Eldritch Blast",
                category="class", combat_relevant=True, automated=True,
                notes="Uses the universal ranged spell-attack and force-damage primitives.",
            ),
            FeatureAudit(
                feature_id="hex", feature_name="Hex",
                source_reference="D&D Basic Rules 2014: Hex",
                category="class", combat_relevant=True, automated=True,
                notes="Uses the reusable targeted concentration bonus-damage primitive shared with Hunter's Mark.",
            ),
        ]
        if level >= 2:
            audits += [
                FeatureAudit(
                    feature_id="agonizing-blast", feature_name="Agonizing Blast",
                    source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                    category="class", combat_relevant=True, automated=True,
                    notes="Adds Charisma modifier to each certified Eldritch Blast beam.",
                ),
                FeatureAudit(
                    feature_id="eldritch-spear", feature_name="Eldritch Spear",
                    source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                    category="class", combat_relevant=True, automated=True,
                    notes="Extends Eldritch Blast range through the shared range model.",
                ),
            ]
        if level >= 3:
            audits.append(FeatureAudit(
                feature_id="pact-of-the-tome", feature_name="Pact of the Tome",
                source_reference="D&D Basic Rules 2014: Pact Boon — Pact of the Tome",
                category="class", combat_relevant=False, automated=True,
                notes="Canonical blaster boon; bonus utility cantrips remain progression metadata.",
            ))
        if level >= 4:
            audits.append(FeatureAudit(
                feature_id="ability-score-improvement-l4", feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Warlock 4",
                category="class", combat_relevant=True, automated=True,
                notes="Raises Charisma 16→18 through the certified build profile.",
            ))
        if level >= 5:
            audits += [
                FeatureAudit(
                    feature_id="eldritch-blast-second-beam", feature_name="Eldritch Blast — Two Beams",
                    source_reference="D&D Basic Rules 2014: Eldritch Blast",
                    category="class", combat_relevant=True, automated=True,
                    notes="Uses the universal multi-spell-attack sequence.",
                ),
                FeatureAudit(
                    feature_id="mask-of-many-faces", feature_name="Mask of Many Faces",
                    source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                    category="class", combat_relevant=False, automated=True,
                    notes="Arena-neutral utility invocation.",
                ),
            ]
        if level >= 6:
            audits += [
                FeatureAudit(
                    feature_id="dark-ones-own-luck", feature_name="Dark One's Own Luck",
                    source_reference="D&D Basic Rules 2014: The Fiend 6",
                    category="subclass", combat_relevant=True, automated=True,
                    notes="Reuses the resource-backed d20 bonus-die primitive.",
                ),
                FeatureAudit(
                    feature_id="dispel-magic", feature_name="Dispel Magic",
                    source_reference="D&D Basic Rules 2014: Warlock Spell List",
                    category="class", combat_relevant=True, automated=True,
                    notes="Reuses the universal effect-removal action.",
                ),
            ]
        if level >= 7:
            audits.append(FeatureAudit(
                feature_id="book-of-ancient-secrets", feature_name="Book of Ancient Secrets",
                source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                category="class", combat_relevant=False, automated=True,
                notes="Arena-neutral Pact of the Tome utility.",
            ))
        if level >= 8:
            audits.append(FeatureAudit(
                feature_id="ability-score-improvement-l8", feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Warlock 8",
                category="class", combat_relevant=True, automated=True,
                notes="Raises Charisma 18→20 through the certified build profile.",
            ))
        return audits
    except Exception:
        logger.exception("Failed to build Varek's low-level 2014 Fiend audits at level %s.", level)
        raise

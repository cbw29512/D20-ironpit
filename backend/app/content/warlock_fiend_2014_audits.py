from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def build_varek_fiend_2014_audits(level: int) -> list[FeatureAudit]:
    audits = [
        FeatureAudit(
            feature_id="pact-magic", feature_name="Pact Magic",
            source_reference="D&D Basic Rules 2014: Warlock 1",
            category="class", combat_relevant=True, automated=True,
            notes="One 1st-level Pact Magic slot is represented by the shared spell-slot resource model.",
        ),
        FeatureAudit(
            feature_id="fiend-patron", feature_name="The Fiend",
            source_reference="D&D Basic Rules 2014: Otherworldly Patron — The Fiend",
            category="subclass", combat_relevant=True, automated=True,
            notes="2014 patron begins at level 1; Expanded Spell List adds choices rather than automatic known spells.",
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
            notes="Selected for the damage-first canonical build. Uses the reusable targeted concentration bonus-damage primitive shared with Hunter's Mark.",
        ),
    ]
    if level >= 2:
        audits.extend([
            FeatureAudit(
                feature_id="agonizing-blast", feature_name="Agonizing Blast",
                source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                category="class", combat_relevant=True, automated=True,
                notes="Adds Charisma modifier to each certified Eldritch Blast beam through the spell-attack damage bonus field.",
            ),
            FeatureAudit(
                feature_id="eldritch-spear", feature_name="Eldritch Spear",
                source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                category="class", combat_relevant=True, automated=True,
                notes="Extends Eldritch Blast range to 300 feet without a new resolver.",
            ),
        ])
    if level >= 3:
        audits.append(
            FeatureAudit(
                feature_id="pact-of-the-tome", feature_name="Pact of the Tome",
                source_reference="D&D Basic Rules 2014: Pact Boon — Pact of the Tome",
                category="class", combat_relevant=False, automated=True,
                notes=(
                    "Canonical blaster boon. Its three bonus cantrips are retained as progression metadata; "
                    "Eldritch Blast remains the stronger certified arena attack, so Tome does not require a new resolver."
                ),
            )
        )
    if level >= 4:
        audits.append(
            FeatureAudit(
                feature_id="ability-score-improvement-l4", feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Warlock 4",
                category="class", combat_relevant=True, automated=True,
                notes="Damage-first progression raises Charisma 16→18, improving spell attacks, save DC, and Agonizing Blast damage.",
            )
        )
    if level >= 5:
        audits.extend([
            FeatureAudit(
                feature_id="eldritch-blast-second-beam", feature_name="Eldritch Blast — Two Beams",
                source_reference="D&D Basic Rules 2014: Eldritch Blast",
                category="class", combat_relevant=True, automated=True,
                notes="Uses the universal multi-spell-attack sequence; each beam gets its own attack roll, crit, defenses, and damage riders.",
            ),
            FeatureAudit(
                feature_id="mask-of-many-faces", feature_name="Mask of Many Faces",
                source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                category="class", combat_relevant=False, automated=True,
                notes="Third invocation is retained as arena-neutral utility so the blaster build does not add low-value bespoke combat mechanics.",
            ),
        ])
    if level >= 6:
        audits.extend([
            FeatureAudit(
                feature_id="dark-ones-own-luck", feature_name="Dark One's Own Luck",
                source_reference="D&D Basic Rules 2014: The Fiend 6",
                category="subclass", combat_relevant=True, automated=True,
                notes="Reuses the resource-backed d20 bonus-die primitive for one d10 on a failed ability check or saving throw when the roll can be rescued.",
            ),
            FeatureAudit(
                feature_id="dispel-magic", feature_name="Dispel Magic",
                source_reference="D&D Basic Rules 2014: Warlock Spell List",
                category="class", combat_relevant=True, automated=True,
                notes="Selected when no new simple damage spell improves on the level-5 blaster package; reuses the universal effect-removal action.",
            ),
        ])
    if level >= 7:
        audits.append(
            FeatureAudit(
                feature_id="book-of-ancient-secrets", feature_name="Book of Ancient Secrets",
                source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                category="class", combat_relevant=False, automated=True,
                notes="Fourth invocation reinforces Pact of the Tome utility without adding a weaker arena action than the blaster package.",
            )
        )
    if level >= 8:
        audits.append(
            FeatureAudit(
                feature_id="ability-score-improvement-l8", feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Warlock 8",
                category="class", combat_relevant=True, automated=True,
                notes="Damage-first progression raises Charisma 18→20 for maximum spell attack, save DC, and Agonizing Blast damage.",
            )
        )
    if level >= 9:
        audits.extend([
            FeatureAudit(
                feature_id="flame-strike", feature_name="Flame Strike",
                source_reference="D&D Basic Rules 2014: The Fiend Expanded Spell List",
                category="subclass", combat_relevant=True, automated=True,
                notes="Damage-first level-9 choice reuses the universal multi-component area save-damage primitive.",
            ),
            FeatureAudit(
                feature_id="whispers-of-the-grave", feature_name="Whispers of the Grave",
                source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                category="class", combat_relevant=False, automated=True,
                notes="Fifth invocation is arena-neutral utility; Varek keeps his combat actions focused on higher-DPR blaster options.",
            ),
        ])
    if level >= 10:
        audits.append(
            FeatureAudit(
                feature_id="fiendish-resilience", feature_name="Fiendish Resilience",
                source_reference="D&D Basic Rules 2014: The Fiend 10",
                category="subclass", combat_relevant=True, automated=True,
                notes=(
                    "Uses the generic precombat best-resistance selector and fight-scoped conditional damage defense; "
                    "magical and silvered weapon damage bypass the selected resistance per 2014 RAW."
                ),
            )
        )
    if level >= 11:
        audits.extend([
            FeatureAudit(
                feature_id="eldritch-blast-third-beam", feature_name="Eldritch Blast — Three Beams",
                source_reference="D&D Basic Rules 2014: Eldritch Blast",
                category="class", combat_relevant=True, automated=True,
                notes="The universal multi-spell-attack sequence resolves three independent Eldritch Blast beams.",
            ),
            FeatureAudit(
                feature_id="mystic-arcanum-6", feature_name="Mystic Arcanum (6th Level)",
                source_reference="D&D Basic Rules 2014: Warlock 11",
                category="class", combat_relevant=True, automated=True,
                notes="Circle of Death uses a separate one-use resource and the universal resource-backed area-save primitive.",
            ),
        ])
    if level >= 12:
        audits.extend([
            FeatureAudit(
                feature_id="ability-score-improvement-l12", feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Warlock 12",
                category="class", combat_relevant=True, automated=True,
                notes="With Charisma already 20, Constitution 14→16 raises HP and concentration durability to preserve Hex damage uptime.",
            ),
            FeatureAudit(
                feature_id="eyes-of-the-rune-keeper", feature_name="Eyes of the Rune Keeper",
                source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                category="class", combat_relevant=False, automated=True,
                notes="Sixth invocation is arena-neutral rather than adding a low-value bespoke combat mechanic.",
            ),
        ])
    if level >= 13:
        audits.append(
            FeatureAudit(
                feature_id="mystic-arcanum-7", feature_name="Mystic Arcanum (7th Level)",
                source_reference="D&D Basic Rules 2014: Warlock 13; Finger of Death",
                category="class", combat_relevant=True, automated=True,
                notes=(
                    "Finger of Death reuses the universal resource-backed save-damage action. "
                    "Its post-kill zombie creation is arena-inert under the summon contract."
                ),
            )
        )
    if level >= 14:
        audits.append(
            FeatureAudit(
                feature_id="hurl-through-hell", feature_name="Hurl Through Hell",
                source_reference="D&D Basic Rules 2014: The Fiend 14",
                category="subclass", combat_relevant=True, automated=True,
                notes=(
                    "A qualifying hit spends its once-per-rest resource, applies the universal Banished/exile state, "
                    "removes the target from battlefield targeting until the end of the source's next turn, then deals "
                    "10d10 psychic damage on return unless the target is a fiend."
                ),
            )
        )
    return audits

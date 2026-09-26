from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def build_druid_land_2014_feature_audits(level: int) -> list[FeatureAudit]:
    if level not in range(1, 21):
        raise ValueError("2014 Land Druid feature audit covers levels 1 through 20.")
    rows = [
        FeatureAudit(
            feature_id="wood-elf", feature_name="Wood Elf",
            source_reference="D&D Basic Rules 2014: Wood Elf",
            category="species", combat_relevant=True, automated=True,
            notes=(
                "DEX +2, WIS +1, 35-foot speed, Keen Senses, and Fey Ancestry are "
                "bound through shared stat/skill/save-modifier primitives."
            ),
        ),
        FeatureAudit(
            feature_id="scimitar", feature_name="Scimitar",
            source_reference="D&D Basic Rules 2014: Equipment",
            category="equipment", combat_relevant=True, automated=True,
            runtime_attack_weapon_id="scimitar",
        ),
        FeatureAudit(
            feature_id="spellcasting", feature_name="Spellcasting",
            source_reference="D&D Basic Rules 2014: Druid 1",
            category="class", combat_relevant=True, automated=True,
        ),
        FeatureAudit(
            feature_id="druidic", feature_name="Druidic",
            source_reference="D&D Basic Rules 2014: Druid 1",
            category="class", combat_relevant=False, automated=True,
        ),
    ]
    if level >= 2:
        rows += [
            FeatureAudit(
                feature_id="wild-shape", feature_name="Wild Shape",
                source_reference="D&D Basic Rules 2014: Druid 2",
                category="class", combat_relevant=True, automated=True,
                notes=(
                    "Uses the universal replacement-form action/lifecycle with certified 2014 beast data, "
                    "separate form HP, automatic reversion, excess-damage carryover, and concentration persistence."
                ),
            ),
            FeatureAudit(
                feature_id="circle-land", feature_name="Circle of the Land",
                source_reference="D&D Basic Rules 2014: Circle of the Land",
                category="subclass", combat_relevant=False, automated=True,
                notes="Subclass identity is a sparse overlay; its level-2 combat-neutral choices do not replace base Druid features.",
            ),
            FeatureAudit(
                feature_id="bonus-cantrip", feature_name="Bonus Cantrip",
                source_reference="D&D Basic Rules 2014: Circle of the Land 2",
                category="subclass", combat_relevant=False, automated=True,
                notes="Canonical Land build selects Mending as the arena-neutral bonus cantrip.",
            ),
            FeatureAudit(
                feature_id="natural-recovery", feature_name="Natural Recovery",
                source_reference="D&D Basic Rules 2014: Circle of the Land 2",
                category="subclass", combat_relevant=False, automated=True,
                notes="Rest-time recovery is outside an in-progress Iron Pit fight.",
            ),
        ]
    if level >= 3:
        rows.append(
            FeatureAudit(
                feature_id="circle-spells-2",
                feature_name="Circle Spells (Forest, 2nd level)",
                source_reference="D&D Basic Rules 2014: Circle of the Land — Forest",
                category="subclass",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Forest grants Barkskin and Spider Climb. Barkskin uses the universal minimum-AC "
                    "modifier; Spider Climb is arena-neutral on the flat Iron Pit battlefield."
                ),
            )
        )
    if level >= 4:
        rows += [
            FeatureAudit(
                feature_id="ability-score-improvement-4",
                feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Druid 4",
                category="class",
                combat_relevant=True,
                automated=True,
                notes="Canonical progression raises Wisdom by 2 and recomputes spell attack/save and Wisdom skills.",
            ),
            FeatureAudit(
                feature_id="wild-shape-improvement-4",
                feature_name="Wild Shape Improvement",
                source_reference="D&D Basic Rules 2014: Druid 4",
                category="class",
                combat_relevant=True,
                automated=True,
                notes="Canonical form advances to the certified CR 1/2 Crocodile and permits swimming forms.",
            ),
        ]
    if level >= 5:
        rows.append(
            FeatureAudit(
                feature_id="circle-spells-3",
                feature_name="Circle Spells (Forest, 3rd level)",
                source_reference="D&D Basic Rules 2014: Circle of the Land — Forest",
                category="subclass",
                combat_relevant=False,
                automated=False,
                notes=(
                    "Forest grants Call Lightning and Plant Growth, both preserved in source metadata. "
                    "Plant Growth has no normal plants to affect on the default Pit battlefield. Call Lightning "
                    "requires vertical storm-cloud placement that the standard x/y-only, horizontal-flight Pit "
                    "does not model, so Arena AI never selects it. Neither unavailable spell blocks certification."
                ),
            )
        )
    if level >= 6:
        rows.append(
            FeatureAudit(
                feature_id="lands-stride",
                feature_name="Land's Stride",
                source_reference="D&D Basic Rules 2014: Circle of the Land 6",
                category="subclass",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Reuses the universal nonmagical Difficult Terrain counter and tagged saving-throw "
                    "Advantage for magical plant impediments; no Druid-specific resolver."
                ),
            )
        )
    if level >= 7:
        rows.append(
            FeatureAudit(
                feature_id="circle-spells-4",
                feature_name="Circle Spells (Forest, 4th level)",
                source_reference="D&D Basic Rules 2014: Circle of the Land — Forest",
                category="subclass",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Forest grants Divination and Freedom of Movement. Divination is arena-neutral. "
                    "Freedom of Movement reuses the shared 2014 defensive-spell debuff-counter composition."
                ),
            )
        )
    return rows

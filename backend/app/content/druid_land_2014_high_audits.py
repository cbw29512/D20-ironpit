from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def build_druid_land_2014_high_feature_audits(level: int) -> list[FeatureAudit]:
    rows: list[FeatureAudit] = []
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
    if level >= 8:
        rows += [
            FeatureAudit(
                feature_id="ability-score-improvement-8",
                feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Druid 8",
                category="class",
                combat_relevant=True,
                automated=True,
                notes="Canonical progression raises Wisdom from 18 to 20 and recompiles Wisdom-derived combat values.",
            ),
            FeatureAudit(
                feature_id="wild-shape-improvement-8",
                feature_name="Wild Shape Improvement",
                source_reference="D&D Basic Rules 2014: Druid 8",
                category="class",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Canonical form advances to the certified CR 1 Brown Bear. The source progression permits "
                    "flying forms, while the standard Pit still applies its universal horizontal-flight arena rule."
                ),
            ),
        ]
    if level >= 9:
        rows.append(
            FeatureAudit(
                feature_id="circle-spells-5",
                feature_name="Circle Spells (Forest, 5th level)",
                source_reference="D&D Basic Rules 2014: Circle of the Land — Forest",
                category="subclass",
                combat_relevant=False,
                automated=False,
                notes=(
                    "Forest grants Commune with Nature and Tree Stride. Commune with Nature is noncombat; "
                    "Tree Stride has no legal destination trees on the default Pit battlefield. Both remain "
                    "preserved in source metadata and do not block standard-arena certification."
                ),
            )
        )
    if level >= 10:
        rows.append(
            FeatureAudit(
                feature_id="natures-ward",
                feature_name="Nature's Ward",
                source_reference="D&D Basic Rules 2014: Circle of the Land 10",
                category="subclass",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Uses universal checks only: poison damage immunity, passive Poisoned/disease debuff "
                    "prevention, and source-typed Charmed/Frightened immunity against Fey and Elementals."
                ),
            )
        )
    if level >= 12:
        rows.append(
            FeatureAudit(
                feature_id="ability-score-improvement-12",
                feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Druid 12",
                category="class",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Canonical progression raises Constitution from 14 to 16; shared character math "
                    "recomputes maximum HP with the new modifier."
                ),
            )
        )
    if level >= 14:
        rows.append(
            FeatureAudit(
                feature_id="natures-sanctuary",
                feature_name="Nature's Sanctuary",
                source_reference="D&D Basic Rules 2014: Circle of the Land 14",
                category="subclass",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Uses the universal targeting-save gate with Beast/Plant source filtering. "
                    "A successful Wisdom save records the source creature's printed 24-hour immunity "
                    "as fresh per-fight targeting-gate state; no Druid-specific resolver."
                ),
            )
        )
    if level >= 16:
        rows.append(
            FeatureAudit(
                feature_id="ability-score-improvement-16",
                feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Druid 16",
                category="class",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Canonical progression raises Constitution from 16 to 18; shared character math "
                    "recomputes maximum HP with the new modifier."
                ),
            )
        )
    if level >= 18:
        rows += [
            FeatureAudit(
                feature_id="timeless-body",
                feature_name="Timeless Body",
                source_reference="D&D Basic Rules 2014: Druid 18",
                category="class",
                combat_relevant=False,
                automated=True,
                notes="Aging rate has no effect on an Iron Pit combat result.",
            ),
            FeatureAudit(
                feature_id="beast-spells",
                feature_name="Beast Spells",
                source_reference="D&D Basic Rules 2014: Druid 18",
                category="class",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Reuses the universal replacement-form spell legality filter. While Wild Shaped, "
                    "only Druid spell actions that do not require material components are retained."
                ),
            ),
        ]
    if level >= 19:
        rows.append(
            FeatureAudit(
                feature_id="ability-score-improvement-19",
                feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Druid 19",
                category="class",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Canonical progression raises Dexterity from 15 to 17; shared character math "
                    "recomputes AC and initiative."
                ),
            )
        )
    if level >= 20:
        rows.append(
            FeatureAudit(
                feature_id="archdruid",
                feature_name="Archdruid",
                source_reference="D&D Basic Rules 2014: Druid 20",
                category="class",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Wild Shape uses the universal unlimited-resource path. The replacement-form spell "
                    "allowlist expands to spells whose otherwise-blocking noncost material components "
                    "are ignored by Archdruid; no Druid-specific spell resolver is added."
                ),
            )
        )
    return rows

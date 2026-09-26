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
        rows += [
            FeatureAudit(
                feature_id="college-lore", feature_name="College of Lore",
                source_reference="D&D Basic Rules 2014: College of Lore",
                category="subclass", combat_relevant=False, automated=True,
            ),
            FeatureAudit(
                feature_id="cutting-words", feature_name="Cutting Words",
                source_reference="D&D Basic Rules 2014: College of Lore 3",
                category="subclass", combat_relevant=True, automated=True,
            ),
            FeatureAudit(
                feature_id="expertise", feature_name="Expertise",
                source_reference="D&D Basic Rules 2014: Bard 3",
                category="class", combat_relevant=False, automated=True,
                notes="Canonical expertise choices are Performance and Persuasion.",
            ),
        ]
    if level >= 5:
        rows.append(FeatureAudit(
            feature_id="font-of-inspiration", feature_name="Font of Inspiration",
            source_reference="D&D Basic Rules 2014: Bard 5",
            category="class", combat_relevant=False, automated=True,
            notes="Iron Pit resets resources between matches; short-rest recovery does not change in-fight resolution.",
        ))
    if level >= 6:
        rows += [
            FeatureAudit(
                feature_id="countercharm", feature_name="Countercharm",
                source_reference="D&D Basic Rules 2014: Bard 6",
                category="class", combat_relevant=True, automated=True,
                notes=(
                    "Uses the universal timed friendly save-aura buff. Iron Pit may spend the "
                    "single free opening-buff activation before initiative; later activation "
                    "uses Countercharm's normal Action cost."
                ),
            ),
            FeatureAudit(
                feature_id="additional-magical-secrets",
                feature_name="Additional Magical Secrets",
                source_reference="D&D Basic Rules 2014: College of Lore 6",
                category="subclass", combat_relevant=True, automated=True,
                notes="Canonical bonus-known selections are Bless and Spiritual Weapon.",
            ),
        ]
    if level >= 10:
        rows += [
            FeatureAudit(
                feature_id="expertise-2", feature_name="Expertise",
                source_reference="D&D Basic Rules 2014: Bard 10",
                category="class", combat_relevant=True, automated=True,
                notes=(
                    "Second Expertise choices are Acrobatics and Perception. "
                    "Acrobatics affects certified grapple-escape checks."
                ),
            ),
            FeatureAudit(
                feature_id="magical-secrets", feature_name="Magical Secrets",
                source_reference="D&D Basic Rules 2014: Bard 10",
                category="class", combat_relevant=True, automated=True,
                notes="Canonical selections are Flame Strike and Death Ward.",
            ),
        ]
    if level >= 14:
        rows += [
            FeatureAudit(
                feature_id="magical-secrets-2", feature_name="Magical Secrets",
                source_reference="D&D Basic Rules 2014: Bard 14",
                category="class", combat_relevant=True, automated=True,
                notes="Canonical selections are Guiding Bolt and Shield of Faith; both reuse shared spell primitives.",
            ),
            FeatureAudit(
                feature_id="peerless-skill", feature_name="Peerless Skill",
                source_reference="D&D Basic Rules 2014: College of Lore 14",
                category="subclass", combat_relevant=True, automated=True,
                notes="Reuses the universal resource-backed d20 bonus-die trigger for ability checks.",
            ),
        ]
    if level >= 18:
        rows.append(FeatureAudit(
            feature_id="magical-secrets-3", feature_name="Magical Secrets",
            source_reference="D&D Basic Rules 2014: Bard 18",
            category="class", combat_relevant=True, automated=True,
            notes="Canonical selections are Aid and Inflict Wounds; both reuse shared universal spell primitives.",
        ))
    return rows

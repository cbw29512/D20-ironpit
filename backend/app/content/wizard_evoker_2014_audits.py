from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def build_wizard_evoker_2014_feature_audits(level: int) -> list[FeatureAudit]:
    if level not in range(1, 21):
        raise ValueError("2014 Evoker Wizard audits currently cover levels 1 through 20.")
    rows = [
        FeatureAudit(
            feature_id="human", feature_name="Human",
            source_reference="D&D Basic Rules 2014: Human",
            category="species", combat_relevant=True, automated=True,
            notes="Standard Human +1 to all six ability scores is compiled into immutable build data.",
        ),
        FeatureAudit(
            feature_id="dagger", feature_name="Dagger",
            source_reference="D&D Basic Rules 2014: Equipment",
            category="equipment", combat_relevant=True, automated=True,
            runtime_attack_weapon_id="dagger",
        ),
        FeatureAudit(
            feature_id="wizard-spellcasting", feature_name="Spellcasting",
            source_reference="D&D Basic Rules 2014: Wizard 1",
            category="class", combat_relevant=True, automated=True,
            notes="Prepared spell count, cantrips, spell slots, save DC, and spell attack use shared caster primitives.",
        ),
        FeatureAudit(
            feature_id="arcane-recovery", feature_name="Arcane Recovery",
            source_reference="D&D Basic Rules 2014: Wizard 1",
            category="class", combat_relevant=False, automated=True,
            notes="Requires a short rest and therefore does not alter a single Iron Pit combat encounter.",
        ),
    ]
    if level >= 2:
        rows.extend([
            FeatureAudit(
                feature_id="evocation-savant", feature_name="Evocation Savant",
                source_reference="D&D Basic Rules 2014: School of Evocation 2",
                category="subclass", combat_relevant=False, automated=True,
                notes="Spellbook copying time and gold are outside arena combat.",
            ),
            FeatureAudit(
                feature_id="sculpt-spells", feature_name="Sculpt Spells",
                source_reference="D&D Basic Rules 2014: School of Evocation 2",
                category="subclass", combat_relevant=True, automated=True,
                notes=(
                    "Uses the universal area-spell ally-protection grant. Eligible allies are source-visible, "
                    "the per-cast protection cap is 1 + slot level, protected creatures are omitted from damage "
                    "resolution, and the source name remains Sculpt Spells in audit data."
                ),
            ),
        ])
    if level >= 4:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-4", feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Wizard 4",
            category="class", combat_relevant=True, automated=True,
            notes="+2 Intelligence raises spell attack, spell save DC, Intelligence saves/skills, and prepared-spell count.",
        ))
    if level >= 6:
        rows.append(FeatureAudit(
            feature_id="potent-cantrip", feature_name="Potent Cantrip",
            source_reference="D&D Basic Rules 2014: School of Evocation 6",
            category="subclass", combat_relevant=True, automated=True,
            notes="Save-based damaging cantrips reuse the universal half-damage-on-success spell outcome.",
        ))
    if level >= 8:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-8", feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Wizard 8",
            category="class", combat_relevant=True, automated=True,
            notes="+2 Intelligence reaches INT 20 and updates all derived caster values.",
        ))
    if level >= 10:
        rows.append(FeatureAudit(
            feature_id="empowered-evocation", feature_name="Empowered Evocation",
            source_reference="D&D Basic Rules 2014: School of Evocation 10",
            category="subclass", combat_relevant=True, automated=True,
            notes="Canonical Evocation damage spells add Intelligence modifier once to their shared damage roll.",
        ))
    if level >= 12:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-12", feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Wizard 12",
            category="class", combat_relevant=True, automated=True,
            notes="+2 Constitution improves Constitution saves and retroactive maximum HP.",
        ))
    if level >= 14:
        rows.append(FeatureAudit(
            feature_id="overchannel", feature_name="Overchannel",
            source_reference="D&D Basic Rules 2014: School of Evocation 14",
            category="subclass", combat_relevant=True, automated=True,
            notes=(
                "Binds to the universal spell-damage maximizer: declared 1st-5th-level damaging spells "
                "use maximum damage dice; fresh per-fight usage state makes the first use safe, then "
                "resolves escalating d12 necrotic self-damage after later casts without defense reduction."
            ),
        ))
    if level >= 16:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-16", feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Wizard 16",
            category="class", combat_relevant=True, automated=True,
            notes="+2 Constitution improves durability through shared derived-stat math.",
        ))
    if level >= 18:
        rows.append(FeatureAudit(
            feature_id="spell-mastery", feature_name="Spell Mastery",
            source_reference="D&D Basic Rules 2014: Wizard 18",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "Burning Hands and Shatter bind to reusable alternate spell-cast grants. "
                "Each retains its printed level and action but does not expend a spell slot."
            ),
        ))
    if level >= 19:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement-19", feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Wizard 19",
            category="class", combat_relevant=True, automated=True,
            notes="+1 Constitution and +1 Wisdom improve durability and saving throws.",
        ))
    if level >= 20:
        rows.append(FeatureAudit(
            feature_id="signature-spells", feature_name="Signature Spells",
            source_reference="D&D Basic Rules 2014: Wizard 20",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "Fireball and Lightning Bolt each bind to a reusable fixed-level alternate cast "
                "backed by an independent one-use Signature Spells resource."
            ),
        ))
    return rows

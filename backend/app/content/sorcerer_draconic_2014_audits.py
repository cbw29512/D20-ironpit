from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def build_sorcerer_draconic_2014_feature_audits(level: int) -> list[FeatureAudit]:
    if level not in range(1, 17):
        raise ValueError("2014 Draconic Sorcerer audits currently cover levels 1 through 16.")
    rows = [
        FeatureAudit(
            feature_id="half-elf", feature_name="Half-Elf",
            source_reference="D&D Basic Rules 2014: Half-Elf",
            category="species", combat_relevant=True, automated=True,
            notes="Ability increases and Fey Ancestry reuse shared score and contextual save-advantage mechanics.",
        ),
        FeatureAudit(
            feature_id="light-crossbow", feature_name="Light Crossbow",
            source_reference="D&D Basic Rules 2014: Equipment",
            category="equipment", combat_relevant=True, automated=True,
            runtime_attack_weapon_id="light-crossbow",
        ),
        FeatureAudit(
            feature_id="spellcasting", feature_name="Spellcasting",
            source_reference="D&D Basic Rules 2014: Sorcerer 1",
            category="class", combat_relevant=True, automated=True,
            notes="Two 1st-level slots, four cantrips, and two known spells bind to shared spell attack/save primitives.",
        ),
        FeatureAudit(
            feature_id="draconic-resilience", feature_name="Draconic Resilience",
            source_reference="D&D Basic Rules 2014: Draconic Bloodline 1",
            category="subclass", combat_relevant=True, automated=True,
            notes="Compiled directly into max HP (+1 per Sorcerer level) and unarmored AC (13 + Dexterity modifier).",
        ),
        FeatureAudit(
            feature_id="dragon-ancestor", feature_name="Dragon Ancestor",
            source_reference="D&D Basic Rules 2014: Draconic Bloodline 1",
            category="subclass", combat_relevant=False, automated=True,
            notes="Language and Charisma interaction are arena-neutral at level 1.",
        ),
    ]
    if level >= 2:
        rows.append(FeatureAudit(
            feature_id="font-of-magic", feature_name="Font of Magic",
            source_reference="D&D Basic Rules 2014: Sorcerer 2",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "Flexible Casting binds to the universal resource-conversion action: normal Bonus Action cost, "
                "finite resource spending, bounded Sorcery Point gains, and temporary spell-slot overflow."
            ),
        ))
    if level >= 3:
        rows += [
            FeatureAudit(
                feature_id="heightened-spell", feature_name="Metamagic: Heightened Spell",
                source_reference="D&D Basic Rules 2014: Sorcerer 3",
                category="class", combat_relevant=True, automated=True,
                notes=(
                    "Spends 3 Sorcery Points through the universal resource system and supplies one contextual "
                    "Disadvantage source to the first actual target saving against the spell."
                ),
            ),
            FeatureAudit(
                feature_id="subtle-spell", feature_name="Metamagic: Subtle Spell",
                source_reference="D&D Basic Rules 2014: Sorcerer 3",
                category="class", combat_relevant=False, automated=True,
                notes=(
                    "The current Pit does not model verbal/somatic suppression or perceptible casting as a "
                    "combat legality gate, so removing those components is arena-neutral."
                ),
            ),
        ]
    if level >= 4:
        rows.append(FeatureAudit(
            feature_id="ability-score-improvement",
            feature_name="Ability Score Improvement",
            source_reference="D&D Basic Rules 2014: Sorcerer 4",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "+2 Charisma raises Nyra from 17 to 19, increasing spell attack, spell save DC, "
                "Charisma saves, and Charisma-based skill bonuses through shared derived-stat math."
            ),
        ))
    if level >= 5:
        rows.append(FeatureAudit(
            feature_id="fireball",
            feature_name="Fireball",
            source_reference="D&D Basic Rules 2014: Fireball",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "Uses the universal point-origin radius area, Dexterity saving throw, fire damage, "
                "half-on-success, and per-slot-level upcast scaling."
            ),
        ))
    if level >= 6:
        rows.append(FeatureAudit(
            feature_id="elemental-affinity",
            feature_name="Elemental Affinity",
            source_reference="D&D Basic Rules 2014: Draconic Bloodline 6",
            category="subclass", combat_relevant=True, automated=True,
            notes=(
                "Fire ancestry adds Charisma modifier to one fire-spell damage roll through the normal "
                "spell damage bonus field. A qualifying cast may spend 1 Sorcery Point through the universal "
                "spell-cast timed-resistance trigger to gain fire resistance for 1 hour."
            ),
        ))
    if level >= 7:
        rows.append(FeatureAudit(
            feature_id="greater-invisibility",
            feature_name="Greater Invisibility",
            source_reference="D&D Basic Rules 2014: Greater Invisibility",
            category="class", combat_relevant=True, automated=True,
            notes=(
                "Reuses the shared 2014 defensive-spell path, Invisible condition, concentration lifecycle, "
                "and Iron Pit opening-buff policy."
            ),
        ))
    if level >= 8:
        rows += [
            FeatureAudit(
                feature_id="ability-score-improvement-8",
                feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Sorcerer 8",
                category="class", combat_relevant=True, automated=True,
                notes=(
                    "+1 Charisma / +1 Constitution reaches CHA 20 and CON 12. Shared derived-stat math "
                    "updates spell attack/DC, Charisma saves/skills, Constitution saves, and retroactive HP."
                ),
            ),
            FeatureAudit(
                feature_id="dispel-magic",
                feature_name="Dispel Magic",
                source_reference="D&D Basic Rules 2014: Dispel Magic",
                category="class", combat_relevant=True, automated=True,
                notes="Reuses the existing universal effect-removal action and spell-slot resource path.",
            ),
        ]
    if level >= 9:
        rows.append(FeatureAudit(
            feature_id="creation",
            feature_name="Creation",
            source_reference="D&D Basic Rules 2014: Creation",
            category="class", combat_relevant=False, automated=True,
            notes="Legal fifth-level Sorcerer spell choice recorded as arena-neutral; no combat resolver is required.",
        ))
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
                feature_id="teleportation-circle",
                feature_name="Teleportation Circle",
                source_reference="D&D Basic Rules 2014: Teleportation Circle",
                category="class", combat_relevant=False, automated=True,
                notes="Legal Sorcerer choice; one-minute casting time and travel purpose are arena-neutral.",
            ),
        ]
    if level >= 11:
        rows.append(FeatureAudit(
            feature_id="move-earth",
            feature_name="Move Earth",
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
            feature_id="teleport",
            feature_name="Teleport",
            source_reference="D&D Basic Rules 2014: Teleport",
            category="class", combat_relevant=False, automated=True,
            notes="Legal seventh-level Sorcerer choice recorded as arena-neutral for Iron Pit combat.",
        ))
    if level >= 14:
        rows.append(FeatureAudit(
            feature_id="dragon-wings",
            feature_name="Dragon Wings",
            source_reference="D&D Basic Rules 2014: Draconic Bloodline 14",
            category="subclass", combat_relevant=True, automated=True,
            notes=(
                "Permanent 30-foot flying speed binds directly to the universal movement fingerprint; "
                "no source-name-specific movement resolver is used."
            ),
        ))
    if level >= 15:
        rows.append(FeatureAudit(
            feature_id="tongues",
            feature_name="Tongues",
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
    return rows

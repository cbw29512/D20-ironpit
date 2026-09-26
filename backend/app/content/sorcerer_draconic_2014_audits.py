from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def build_sorcerer_draconic_2014_feature_audits(level: int) -> list[FeatureAudit]:
    if level != 1:
        raise ValueError("2014 Draconic Sorcerer audits currently cover level 1.")
    return [
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

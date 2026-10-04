from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit
from app.domain.targeted_concentration_damage import TargetedConcentrationDamageAction

logger = logging.getLogger(__name__)


def hunters_mark_2024() -> TargetedConcentrationDamageAction:
    try:
        return TargetedConcentrationDamageAction(
            id="hunters-mark",
            name="Hunter's Mark",
            level=1,
            action_cost="bonus_action",
            range_ft=90,
            dice_count=1,
            dice_size=6,
            damage_type="force",
            duration_rounds_by_slot={1: 600, 3: 4800, 5: 14400},
            retarget_after_target_zero=True,
            free_cast_resource_id="favored-enemy-hunters-mark",
            free_cast_resource_cost=1,
            priority=20,
            animation="targeted-concentration",
            source="D&D Beyond Basic Rules 2024: Hunter's Mark",
        )
    except Exception:
        logger.exception("Failed to compile 2024 Hunter's Mark.")
        raise


def build_ranger_2024_level1_audits() -> list[FeatureAudit]:
    try:
        return [
            FeatureAudit(
                feature_id="spellcasting",
                feature_name="Spellcasting",
                source_reference="D&D Beyond Basic Rules 2024: Ranger 1",
                category="class",
                combat_relevant=True,
                automated=True,
                notes="Uses the shared half-caster spell-slot and canonical spell-package rules.",
            ),
            FeatureAudit(
                feature_id="favored-enemy",
                feature_name="Favored Enemy",
                source_reference="D&D Beyond Basic Rules 2024: Ranger 1",
                category="class",
                combat_relevant=True,
                automated=True,
                notes="Hunter's Mark uses the shared targeted concentration bonus-damage primitive with free casts.",
            ),
            FeatureAudit(
                feature_id="weapon-mastery",
                feature_name="Weapon Mastery",
                source_reference="D&D Beyond Basic Rules 2024: Ranger 1",
                category="class",
                combat_relevant=True,
                automated=True,
                notes="Longbow Slow and Shortsword Vex use the universal mastery system.",
            ),
            FeatureAudit(
                feature_id="wood-elf-lineage",
                feature_name="Wood Elf Lineage",
                source_reference="D&D Beyond Basic Rules 2024: Elf — Wood Elf",
                category="species",
                combat_relevant=True,
                automated=True,
                notes="35-foot Speed is runtime-relevant; Druidcraft is arena-neutral.",
            ),
            FeatureAudit(
                feature_id="fey-ancestry",
                feature_name="Fey Ancestry",
                source_reference="D&D Beyond Basic Rules 2024: Elf",
                category="species",
                combat_relevant=True,
                automated=True,
                notes="Uses the shared saving-throw Advantage grant against Charmed effects.",
            ),
            FeatureAudit(
                feature_id="alert",
                feature_name="Alert",
                source_reference="D&D Beyond Basic Rules 2024: Alert",
                category="feat",
                combat_relevant=True,
                automated=True,
                notes="Adds Proficiency Bonus to Initiative; initiative swapping is arena-neutral.",
            ),
            FeatureAudit(
                feature_id="ensnaring-strike",
                feature_name="Ensnaring Strike",
                source_reference="D&D Beyond Basic Rules 2024: Ensnaring Strike",
                category="class",
                combat_relevant=True,
                automated=False,
                notes="Prepared legally but fail-closed pending exact hit-trigger/save/restrained lifecycle composition.",
            ),
        ]
    except Exception:
        logger.exception("Failed to compile 2024 Ranger level 1 feature audits.")
        raise

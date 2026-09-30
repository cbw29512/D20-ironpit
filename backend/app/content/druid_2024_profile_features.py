from __future__ import annotations

import logging

from app.content.druid_2024_progression_audits import (
    build_druid_2024_progression_audits,
    druid_feature_audit,
)
from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def build_druid_2024_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            druid_feature_audit("spellcasting", "Spellcasting", "class", combat_relevant=True, automated=True),
            druid_feature_audit(
                "druidic", "Druidic", "class", combat_relevant=False, automated=True,
                notes="Speak with Animals is always prepared but is arena-neutral.",
            ),
            druid_feature_audit(
                "primal-order-magician", "Primal Order: Magician", "class",
                combat_relevant=False, automated=True,
                notes="Adds one Druid cantrip; the Wisdom-modifier bonus is assigned to Nature.",
            ),
            druid_feature_audit(
                "fey-ancestry", "Fey Ancestry", "species", combat_relevant=True, automated=True,
                notes="Advantage on saves to avoid or end Charmed uses the universal save-advantage primitive.",
            ),
            druid_feature_audit(
                "wood-elf-lineage", "Elven Lineage: Wood Elf", "species",
                combat_relevant=True, automated=True,
                notes="Speed 35 is active; Druidcraft is arena-neutral.",
            ),
            druid_feature_audit(
                "keen-senses", "Keen Senses", "species", combat_relevant=True, automated=True,
                notes="Canonical proficiency choice is Perception.",
            ),
            druid_feature_audit(
                "darkvision", "Darkvision", "species", combat_relevant=False, automated=False,
                notes="Iron Pit assumes sufficient arena visibility.",
            ),
            druid_feature_audit(
                "trance", "Trance", "species", combat_relevant=False, automated=False,
                notes="Long-rest duration does not change a single Iron Pit match.",
            ),
            druid_feature_audit(
                "magic-initiate-cleric", "Magic Initiate (Cleric)", "feat",
                combat_relevant=False, automated=False,
                notes="Canonical choices are Light, Thaumaturgy, and Detect Magic; none alter arena combat.",
            ),
            druid_feature_audit(
                "sickle", "Sickle", "equipment", combat_relevant=True, automated=True,
                runtime_attack_weapon_id="sickle",
            ),
            druid_feature_audit(
                "leather-shield", "Leather Armor and Shield", "equipment",
                combat_relevant=True, automated=True,
            ),
        ]
        if level >= 2:
            audits.extend([
                druid_feature_audit(
                    "wild-shape", "Wild Shape", "class", combat_relevant=True, automated=True,
                    notes=(
                        "2024 Wild Shape reuses the replacement-form engine: Bonus Action, canonical "
                        + ("Brown Bear CR 1 form" if level >= 8 else "Wolf form")
                        + f", owner HP retained, {level} Temporary HP on entry, Humanoid creature type "
                        "retained, and spellcasting unavailable while transformed."
                    ),
                ),
                druid_feature_audit(
                    "wild-companion", "Wild Companion", "class", combat_relevant=False, automated=False,
                    notes=(
                        "Casts Find Familiar by spending a spell slot or Wild Shape use. Creating a separate "
                        "combat entity is globally arena-unavailable, so this option is preserved but not approximated."
                    ),
                ),
            ])
        if level >= 3:
            audits.extend([
                druid_feature_audit(
                    "lands-aid", "Land's Aid", "subclass", combat_relevant=True, automated=True,
                    notes=(
                        "Magic Action spends one Wild Shape use; a point within 60 feet creates a "
                        "10-foot-radius sphere. Chosen creatures make Constitution saves for 2d6 "
                        "Necrotic damage (half on success), and one chosen creature in the area "
                        "independently regains 2d6 HP through the generic area-healing rider."
                    ),
                ),
                druid_feature_audit(
                    "land-arid-spells", "Circle Spells: Arid", "subclass",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Canonical land choice is Arid: Blur, Burning Hands, and Fire Bolt are always "
                        "prepared and use explicit 2024 fingerprints. Blur uses universal "
                        "Blindsight/Truesight bypass ranges rather than unconditional Disadvantage."
                    ),
                ),
            ])
        audits.extend(build_druid_2024_progression_audits(level))
        return audits
    except Exception:
        logger.exception("Failed to build 2024 Druid feature audits for level %s.", level)
        raise

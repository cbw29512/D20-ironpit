from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def _feature(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    combat_relevant: bool,
    automated: bool,
    notes: str | None = None,
    runtime_attack_weapon_id: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_name,
        source_reference="D&D Beyond Basic Rules 2024: Druid / Character Origins",
        category=category,
        combat_relevant=combat_relevant,
        automated=automated,
        notes=notes,
        runtime_attack_weapon_id=runtime_attack_weapon_id,
    )


def build_druid_2024_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _feature("spellcasting", "Spellcasting", "class", combat_relevant=True, automated=True),
            _feature(
                "druidic", "Druidic", "class", combat_relevant=False, automated=True,
                notes="Speak with Animals is always prepared but is arena-neutral.",
            ),
            _feature(
                "primal-order-magician", "Primal Order: Magician", "class",
                combat_relevant=False, automated=True,
                notes="Adds one Druid cantrip; the Wisdom-modifier bonus is assigned to Nature.",
            ),
            _feature(
                "fey-ancestry", "Fey Ancestry", "species", combat_relevant=True, automated=True,
                notes="Advantage on saves to avoid or end Charmed uses the universal save-advantage primitive.",
            ),
            _feature(
                "wood-elf-lineage", "Elven Lineage: Wood Elf", "species",
                combat_relevant=True, automated=True,
                notes="Speed 35 is active; Druidcraft is arena-neutral.",
            ),
            _feature(
                "keen-senses", "Keen Senses", "species", combat_relevant=True, automated=True,
                notes="Canonical proficiency choice is Perception.",
            ),
            _feature(
                "darkvision", "Darkvision", "species", combat_relevant=False, automated=False,
                notes="Iron Pit assumes sufficient arena visibility.",
            ),
            _feature(
                "trance", "Trance", "species", combat_relevant=False, automated=False,
                notes="Long-rest duration does not change a single Iron Pit match.",
            ),
            _feature(
                "magic-initiate-cleric", "Magic Initiate (Cleric)", "feat",
                combat_relevant=False, automated=False,
                notes="Canonical choices are Light, Thaumaturgy, and Detect Magic; none alter arena combat.",
            ),
            _feature(
                "sickle", "Sickle", "equipment", combat_relevant=True, automated=True,
                runtime_attack_weapon_id="sickle",
            ),
            _feature(
                "leather-shield", "Leather Armor and Shield", "equipment",
                combat_relevant=True, automated=True,
            ),
        ]
        if level >= 2:
            audits.extend([
                _feature(
                    "wild-shape", "Wild Shape", "class", combat_relevant=True, automated=True,
                    notes=(
                        "2024 Wild Shape reuses the replacement-form engine: Bonus Action, Wolf form, "
                        "owner HP retained, 2 Temporary HP on entry, Humanoid creature type retained, "
                        "and spellcasting unavailable while transformed."
                    ),
                ),
                _feature(
                    "wild-companion", "Wild Companion", "class", combat_relevant=False, automated=False,
                    notes=(
                        "Casts Find Familiar by spending a spell slot or Wild Shape use. Creating a separate "
                        "combat entity is globally arena-unavailable, so this option is preserved but not approximated."
                    ),
                ),
            ])
        if level >= 3:
            audits.extend([
                _feature(
                    "lands-aid", "Land's Aid", "subclass", combat_relevant=True, automated=True,
                    notes=(
                        "Magic Action spends one Wild Shape use; a point within 60 feet creates a "
                        "10-foot-radius sphere. Chosen creatures make Constitution saves for 2d6 "
                        "Necrotic damage (half on success), and one chosen creature in the area "
                        "independently regains 2d6 HP through the generic area-healing rider."
                    ),
                ),
                _feature(
                    "land-arid-spells", "Circle Spells: Arid", "subclass",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Canonical land choice is Arid: Blur, Burning Hands, and Fire Bolt are always "
                        "prepared and use explicit 2024 fingerprints. Blur uses universal "
                        "Blindsight/Truesight bypass ranges rather than unconditional Disadvantage."
                    ),
                ),
            ])
        if level >= 4:
            audits.append(_feature(
                "ability-score-improvement-l4",
                "Ability Score Improvement (+2 Wisdom)",
                "class",
                combat_relevant=True,
                automated=True,
                notes="Canonical land-damage progression raises Wisdom 17→19 and all derived Druid spell math.",
            ))
        if level >= 5:
            audits.append(_feature(
                "wild-resurgence",
                "Wild Resurgence",
                "class",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Universal resource conversion: at zero Wild Shape, spend one spell slot with no "
                    "action to regain one use, limited once on each turn; alternatively spend one "
                    "Wild Shape plus the once-per-Long-Rest gate to regain one level 1 spell slot."
                ),
            ))
        if level >= 6:
            audits.append(_feature(
                "natural-recovery",
                "Natural Recovery",
                "subclass",
                combat_relevant=True,
                automated=True,
                notes=(
                    "Once per Long Rest, cast one prepared level 1+ Circle Spell without expending "
                    "a spell slot via the universal alternate-spell-cast grant. The Short-Rest slot "
                    "recovery half occurs outside an active Iron Pit match and needs no fight-time resolver."
                ),
            ))
        return audits
    except Exception:
        logger.exception("Failed to build 2024 Druid feature audits for level %s.", level)
        raise

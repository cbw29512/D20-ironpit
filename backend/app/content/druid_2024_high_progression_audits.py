from __future__ import annotations

import logging

from app.content.druid_2024_audit_support import druid_feature_audit
from app.content.druid_2024_final_progression_audits import build_druid_2024_final_progression_audits
from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def build_druid_2024_high_progression_audits(level: int) -> list[FeatureAudit]:
    """Return Druid progression audits introduced at levels 11 through 17."""
    try:
        audits: list[FeatureAudit] = []
        if level >= 11:
            audits.append(druid_feature_audit(
                "druid-combat-spells-6", "Level 6 Spellcasting: Heal", "class",
                combat_relevant=True, automated=True,
                notes=(
                    "Damage/healing-first preparation selects explicit 2024 Heal: Action, 60 feet, "
                    "70 fixed HP restored, and Blinded, Deafened, and Poisoned removed through the "
                    "universal healing action."
                ),
            ))
        if level >= 12:
            audits.append(druid_feature_audit(
                "ability-score-improvement-l12", "Ability Score Improvement (+2 Charisma)", "class",
                combat_relevant=True, automated=True,
                notes=(
                    "Wisdom is already 20, so the canonical land-damage progression uses the repeatable "
                    "Ability Score Improvement feat to raise Charisma 16→18 without changing the prepared "
                    "damage/healing package."
                ),
            ))
        if level >= 13:
            audits.append(druid_feature_audit(
                "druid-combat-spells-7", "Level 7 Spellcasting: Fire Storm", "class",
                combat_relevant=False, automated=True,
                notes=(
                    "Damage-first preparation selects 2024 Fire Storm. Its 7d10 Fire damage and Dexterity "
                    "save are source-audited, but the spell's freely arranged ten contiguous 10-foot cubes "
                    "require multi-cube battlefield geometry that Iron Pit does not yet model exactly. "
                    "It is therefore preserved as arena-out-of-scope instead of approximated."
                ),
            ))
        if level >= 14:
            audits.append(druid_feature_audit(
                "natures-sanctuary", "Nature's Sanctuary", "subclass",
                combat_relevant=True, automated=True,
                notes=(
                    "Universal persistent beneficial-zone composition: spend one Wild Shape with a Magic "
                    "Action to place a 15-foot Cube within 120 feet for 1 minute. Source and allies in the "
                    "zone gain Half Cover (+2 AC and +2 Dexterity saves); allies also gain Arid Fire "
                    "resistance. Bonus Action moves the zone up to 60 feet while remaining within 120 feet."
                ),
            ))
        if level >= 15:
            audits.extend([
                druid_feature_audit(
                    "improved-elemental-fury-potent-spellcasting",
                    "Improved Elemental Fury: Potent Spellcasting",
                    "class",
                    combat_relevant=True,
                    automated=True,
                    notes=(
                        "The existing Druid cantrip actions remain unchanged except for source data range: "
                        "cantrips with a printed range of at least 10 feet gain +300 feet. Poison Spray, "
                        "Fire Bolt, and Starry Wisp therefore compile to 330/420/360 feet; Self-range "
                        "Thunderclap does not qualify. No Druid-named combat resolver is added."
                    ),
                ),
                druid_feature_audit(
                    "druid-combat-spells-8", "Level 8 Spellcasting: Sunburst", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Damage-first preparation selects explicit 2024 Sunburst and reuses the already-certified "
                        "area save-damage plus failed-save timed-condition primitives: Constitution save, 12d6 "
                        "Radiant, half on success, and Blinded for up to 1 minute with an end-of-turn repeat save. "
                        "Its Darkness-dispel clause is arena-inert while Iron Pit has no Dim Light/Darkness state."
                    ),
                ),
            ])
        if level >= 16:
            audits.append(druid_feature_audit(
                "ability-score-improvement-l16", "Ability Score Improvement (+2 Charisma)", "class",
                combat_relevant=True, automated=True,
                notes=(
                    "Wisdom is already 20, so the canonical land-damage progression uses the repeatable "
                    "Ability Score Improvement feat again to raise Charisma 18→20. Spell slots, prepared "
                    "spells, and existing combat actions remain unchanged."
                ),
            ))
        if level >= 17:
            audits.append(druid_feature_audit(
                "druid-combat-spells-9", "Level 9 Spellcasting: Foresight", "class",
                combat_relevant=True, automated=True,
                notes=(
                    "The level-17 damage/healing-first review found no simple 9th-level Druid damage or "
                    "healing spell suitable for exact arena automation: Storm of Vengeance requires a "
                    "round-staged persistent storm subsystem and True Resurrection is combat-inert. The "
                    "canonical build therefore prepares explicit 2024 Foresight. It uses universal D20-test "
                    "Advantage plus attacks-against-Disadvantage modifiers and the Iron Pit free arena-entry "
                    "buff rule, so the legal level-9 slot remains available after precombat setup."
                ),
            ))
        audits.extend(build_druid_2024_final_progression_audits(level))
        return audits
    except Exception:
        logger.exception("Failed to build high-level 2024 Druid progression audits for level %s.", level)
        raise

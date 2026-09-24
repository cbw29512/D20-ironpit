from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)
CLERIC = "D&D Basic Rules 2014: Cleric"
LIFE = "D&D Basic Rules 2014: Life Domain"
DWARF = "D&D Basic Rules 2014: Hill Dwarf"
EQUIPMENT = "D&D Basic Rules 2014: Equipment"

def _audit(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    source: str,
    automated: bool = True,
    combat_relevant: bool = True,
    weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    try:
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=feature_name,
            source_reference=source,
            category=category,
            combat_relevant=combat_relevant,
            automated=automated,
            runtime_attack_weapon_id=weapon_id,
            notes=notes,
        )
    except Exception:
        logger.exception("Failed to build 2014 Life Cleric audit record: %s", feature_id)
        raise


def build_cleric_life_2014_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit("hill-dwarf-constitution", "Dwarf Ability Score Increase", "species", source=DWARF),
            _audit("hill-dwarf-wisdom", "Hill Dwarf Ability Score Increase", "species", source=DWARF),
            _audit(
                "dwarven-resilience", "Dwarven Resilience", "species", source=DWARF,
                notes=(
                    "Dwarf-owned passive buff. Universal resolution checks incoming poison effects/debuffs "
                    "against defender buffs; poison damage resistance stays in the shared damage pipeline."
                ),
            ),
            _audit("dwarven-toughness", "Dwarven Toughness", "species", source=DWARF),
            _audit("spellcasting", "Spellcasting", "class", source=CLERIC),
            _audit("life-domain", "Life Domain", "subclass", source=LIFE),
            _audit("life-domain-heavy-armor", "Bonus Proficiency", "subclass", source=LIFE),
            _audit("disciple-of-life", "Disciple of Life", "subclass", source=LIFE),
            _audit("warhammer", "Warhammer", "equipment", source=EQUIPMENT, weapon_id="warhammer"),
            _audit("scale-mail-shield", "Scale Mail and Shield", "equipment", source=EQUIPMENT),
        ]
        if level >= 2:
            audits.extend([
                _audit("channel-divinity", "Channel Divinity", "class", source=CLERIC),
                _audit(
                    "turn-undead", "Turn Undead", "class", source=CLERIC,
                    notes=(
                        "2014 Iron Pit house rule: failed saves apply the universal Trembling debuff; "
                        "Action, Bonus Action, Reaction, and movement are suppressed until damage or "
                        "an end-of-turn Wisdom save removes the effect."
                    ),
                ),
                _audit(
                    "preserve-life", "Channel Divinity: Preserve Life", "subclass", source=LIFE,
                    notes=(
                        "Uses the universal divisible healing pool with the half-maximum-HP cap and "
                        "2014 Undead/Construct exclusions."
                    ),
                ),
            ])
        if level >= 4:
            audits.append(_audit("asi-4", "Ability Score Improvement", "class", source=CLERIC))
        if level >= 5:
            audits.append(_audit(
                "destroy-undead-half", "Destroy Undead (CR 1/2)", "class", source=CLERIC,
                notes=(
                    "Binds the level-based CR threshold to the shared turning-save resolver; "
                    "eligible failed saves use the universal zero-HP no-damage outcome."
                ),
            ))
        if level >= 6:
            audits.extend([
                _audit("channel-divinity-2", "Channel Divinity (2/rest)", "class", source=CLERIC),
                _audit("blessed-healer", "Blessed Healer", "subclass", source=LIFE),
            ])
        if level >= 8:
            audits.extend([
                _audit("asi-8", "Ability Score Improvement", "class", source=CLERIC),
                _audit(
                    "destroy-undead-1", "Destroy Undead (CR 1)", "class", source=CLERIC,
                    notes="Uses the shared turning-save destruction threshold with CR 1 source data.",
                ),
                _audit(
                    "divine-strike", "Divine Strike", "subclass", source=LIFE,
                    notes="Uses the universal once-per-turn weapon-hit damage rider.",
                ),
            ])
        if level >= 10:
            audits.append(_audit(
                "divine-intervention", "Divine Intervention", "class", source=CLERIC,
                notes=(
                    "Uses the universal percentile-gated healing action. On success, Iron Pit's "
                    "deterministic deity policy restores one legal living party member to effective max HP."
                ),
            ))
        if level >= 11:
            audits.append(_audit(
                "destroy-undead-2", "Destroy Undead (CR 2)", "class", source=CLERIC,
                notes="Uses the shared turning-save destruction threshold with CR 2 source data.",
            ))
        if level >= 12:
            audits.append(_audit("asi-12", "Ability Score Improvement", "class", source=CLERIC))
        if level >= 14:
            audits.extend([
                _audit(
                    "destroy-undead-3", "Destroy Undead (CR 3)", "class", source=CLERIC,
                    automated=False, notes="Depends on the universal Turn Undead resolution path.",
                ),
                _audit(
                    "divine-strike-2d8", "Divine Strike (2d8)", "subclass", source=LIFE,
                    automated=False, notes="Scaling delta of the level-8 once-per-turn weapon-hit damage rider.",
                ),
            ])
        if level >= 16:
            audits.append(_audit("asi-16", "Ability Score Improvement", "class", source=CLERIC))
        if level >= 17:
            audits.extend([
                _audit(
                    "destroy-undead-4", "Destroy Undead (CR 4)", "class", source=CLERIC,
                    automated=False, notes="Depends on the universal Turn Undead resolution path.",
                ),
                _audit(
                    "supreme-healing", "Supreme Healing", "subclass", source=LIFE,
                    notes="Candidate binding to the existing universal healing-maximize semantic.",
                ),
            ])
        if level >= 18:
            audits.append(_audit("channel-divinity-3", "Channel Divinity (3/rest)", "class", source=CLERIC))
        if level >= 19:
            audits.append(_audit("asi-19", "Ability Score Improvement", "class", source=CLERIC))
        if level >= 20:
            audits.append(_audit(
                "divine-intervention-improvement", "Divine Intervention Improvement", "class",
                source=CLERIC, automated=False,
                notes="Requires the same universal Divine Intervention policy as level 10.",
            ))
        return audits
    except Exception:
        logger.exception("Failed to build 2014 Life Cleric feature audits at level %s", level)
        raise

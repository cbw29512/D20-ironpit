from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def _audit(
    feature_id: str,
    name: str,
    category: str,
    *,
    combat: bool = True,
    automated: bool = True,
    weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    try:
        source = "D&D SRD 5.1 (2014): Oath of Devotion" if category == "subclass" else "D&D SRD 5.1 (2014): Paladin"
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=name,
            source_reference=source,
            category=category,
            combat_relevant=combat,
            automated=automated,
            runtime_attack_weapon_id=weapon_id,
            notes=notes,
        )
    except Exception:
        logger.exception("Failed to build 2014 Paladin feature audit for %s", feature_id)
        raise


def build_paladin_2014_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        aura_radius = 30 if level >= 18 else 10
        audits = [
            _audit("human-ability-increase", "Human Ability Score Increase", "species", combat=False),
            _audit("lay-on-hands", "Lay on Hands", "class"),
            _audit("longsword", "Longsword", "equipment", weapon_id="longsword"),
            _audit("shield", "Shield", "equipment"),
            _audit(
                "divine-sense", "Divine Sense", "class", combat=False, automated=False,
                notes="Iron Pit exposes creature identity directly; active detection is outside combat resolution.",
            ),
        ]
        if level >= 2:
            audits.extend([
                _audit("fighting-style-defense", "Defense Fighting Style", "class"),
                _audit(
                    "spellcasting", "Spellcasting", "class",
                    notes=(
                        "Edition-correct prepared spell counts, slots, combat spell actions, Devotion oath spells, "
                        "concentration, condition removal, defensive wards, and Dispel Magic are automated. "
                        "Noncombat utility spells remain explicitly outside arena resolution."
                    ),
                ),
                _audit("divine-smite", "Divine Smite", "class"),
            ])
        if level >= 3:
            audits.extend([
                _audit(
                    "divine-health", "Divine Health", "class", combat=False, automated=False,
                    notes="The standard Iron Pit arena does not apply disease effects.",
                ),
                _audit(
                    "sacred-weapon", "Sacred Weapon", "subclass",
                    notes="Channel Divinity activates the timed Charisma attack-roll bonus through the shared modifier engine.",
                ),
                _audit(
                    "turn-the-unholy", "Turn the Unholy", "subclass",
                    notes="Fiends and Undead within 30 feet use the shared one-minute creature-turning engine.",
                ),
            ])
        if level >= 5:
            audits.append(_audit("extra-attack", "Extra Attack", "class"))
        if level >= 6:
            audits.append(_audit(
                "aura-of-protection", "Aura of Protection", "class",
                notes=f"The strongest Paladin save bonus within {aura_radius} feet is recalculated from live encounter positions.",
            ))
        if level >= 7:
            audits.append(_audit(
                "aura-of-devotion", "Aura of Devotion", "subclass",
                notes=f"Charm immunity propagates dynamically to allies within {aura_radius} feet.",
            ))
        if level >= 10:
            audits.append(_audit(
                "aura-of-courage", "Aura of Courage", "class",
                notes=f"Fear immunity propagates dynamically to allies within {aura_radius} feet.",
            ))
        if level >= 11:
            audits.append(_audit(
                "improved-divine-smite", "Improved Divine Smite", "class",
                notes="Every hit with Aurelia's melee-weapon loadout carries a declarative 1d8 radiant on-hit rider.",
            ))
        if level >= 13:
            audits.extend([
                _audit(
                    "freedom-of-movement", "Freedom of Movement", "subclass",
                    notes="Universal buff/debuff counters implement its arena-relevant movement-control protections.",
                ),
                _audit(
                    "guardian-of-faith", "Guardian of Faith", "subclass",
                    combat=False, automated=False,
                    notes="Always prepared by Oath of Devotion but arena-unavailable while Iron Pit summoning/created combat entities are disabled.",
                ),
                _audit(
                    "death-ward", "Death Ward", "class",
                    notes="Prepared as the legal non-summoning level-4 combat replacement; universal zero-HP replacement consumes the ward on first trigger.",
                ),
            ])
        if level >= 14:
            audits.append(_audit(
                "cleansing-touch", "Cleansing Touch", "class",
                notes=(
                    "Reuses the universal effect-removal action: Action, touch range, "
                    "self/willing ally, no roll, Charisma-modifier uses per long rest."
                ),
            ))
        if level >= 15:
            audits.append(_audit(
                "purity-of-spirit", "Purity of Spirit", "subclass",
                notes=(
                    "Permanent Protection from Evil and Good defenses compile as generic passive modifiers: "
                    "attack Disadvantage plus Charmed/Frightened immunity against aberrations, celestials, "
                    "elementals, fey, fiends, and undead. Possession remains arena-neutral until a certified "
                    "possession mechanic enters active content."
                ),
            ))
        if level >= 17:
            audits.extend([
                _audit(
                    "commune", "Commune", "subclass", combat=False, automated=False,
                    notes="Always prepared by Oath of Devotion but noncombat in the standard Iron Pit.",
                ),
                _audit(
                    "flame-strike", "Flame Strike", "subclass",
                    notes=(
                        "One Dexterity save drives generic 10-foot-radius area damage with independent "
                        "4d6 fire and 4d6 radiant components; each component uses the shared damage pipeline."
                    ),
                ),
            ])
        if level >= 18:
            audits.append(_audit(
                "aura-improvements", "Aura Improvements", "class",
                notes=(
                    "Reuses the existing Aura of Protection, Aura of Courage, and Aura of Devotion "
                    "resolution with the source-owned aura radius increased from 10 feet to 30 feet."
                ),
            ))
        if level >= 19:
            audits.append(_audit(
                "ability-score-improvement-l19",
                "Ability Score Improvement (+1 Charisma, +1 Dexterity)",
                "class",
                notes=(
                    "Split ASI caps Charisma at 20 and raises Dexterity to 12. Aura of Protection, "
                    "Sacred Weapon, Cleansing Touch, spell DC/preparation, Persuasion, initiative, and "
                    "Dexterity-derived values all recompile from the shared ability scores. The Paladin "
                    "slot table also advances to two 5th-level slots."
                ),
            ))
        if level >= 20:
            audits.append(_audit(
                "holy-nimbus", "Holy Nimbus", "subclass",
                notes=(
                    "Action, 1/long rest, 10-round timed self effect. A universal 30-foot enemy-turn-start "
                    "emanation deals 10 radiant damage, while timed source-type-qualified save modifiers grant "
                    "Advantage against spells cast by fiends and undead. No Paladin-specific resolver."
                ),
            ))
        return audits
    except Exception:
        logger.exception("Failed to compile 2014 Paladin feature audits at level %s", level)
        raise

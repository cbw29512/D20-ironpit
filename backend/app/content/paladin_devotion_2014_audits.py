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
                notes="The strongest 10-foot Paladin save bonus is recalculated from live encounter positions.",
            ))
        if level >= 7:
            audits.append(_audit(
                "aura-of-devotion", "Aura of Devotion", "subclass",
                notes="Charm immunity propagates dynamically to allies within 10 feet.",
            ))
        if level >= 10:
            audits.append(_audit(
                "aura-of-courage", "Aura of Courage", "class",
                notes="Fear immunity propagates dynamically to allies within 10 feet.",
            ))
        return audits
    except Exception:
        logger.exception("Failed to compile 2014 Paladin feature audits at level %s", level)
        raise

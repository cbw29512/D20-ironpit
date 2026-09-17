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
                    "spellcasting", "Spellcasting", "class", automated=False,
                    notes="Spell-slot state is modeled; prepared Paladin spell actions still require browser/runtime wiring.",
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
                    "sacred-weapon", "Sacred Weapon", "subclass", automated=False,
                    notes="Channel Divinity state is modeled; timed attack-bonus activation is the next runtime hook.",
                ),
                _audit(
                    "turn-the-unholy", "Turn the Unholy", "subclass", automated=False,
                    notes="Devotion Channel Divinity control is not yet wired into the arena decision policy.",
                ),
            ])
        if level >= 5:
            audits.append(_audit("extra-attack", "Extra Attack", "class"))
        if level >= 6:
            audits.append(_audit(
                "aura-of-protection", "Aura of Protection", "class", automated=False,
                notes="Self saving-throw bonus is modeled; allied 10-foot aura propagation still needs encounter wiring.",
            ))
        if level >= 7:
            audits.append(_audit(
                "aura-of-devotion", "Aura of Devotion", "subclass", automated=False,
                notes="Self charm immunity is modeled; allied aura propagation still needs encounter wiring.",
            ))
        if level >= 10:
            audits.append(_audit(
                "aura-of-courage", "Aura of Courage", "class", automated=False,
                notes="Self fear immunity is modeled; allied aura propagation still needs encounter wiring.",
            ))
        return audits
    except Exception:
        logger.exception("Failed to compile 2014 Paladin feature audits at level %s", level)
        raise

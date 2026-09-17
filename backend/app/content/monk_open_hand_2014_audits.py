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
        source = (
            "D&D SRD 5.1 (2014): Way of the Open Hand"
            if category == "subclass"
            else "D&D SRD 5.1 (2014): Monk"
        )
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
        logger.exception("Failed to build 2014 Monk feature audit for %s", feature_id)
        raise


def build_monk_2014_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit("human-ability-increase", "Human Ability Score Increase", "species", combat=False),
            _audit("unarmored-defense", "Unarmored Defense", "class"),
            _audit("martial-arts", "Martial Arts", "class"),
            _audit("shortsword", "Shortsword", "equipment", weapon_id="shortsword"),
        ]
        if level >= 2:
            audits.extend([
                _audit("ki", "Ki", "class"),
                _audit("flurry-of-blows", "Flurry of Blows", "class"),
                _audit("unarmored-movement", "Unarmored Movement", "class"),
            ])
        if level >= 3:
            audits.extend([
                _audit("deflect-missiles", "Deflect Missiles", "class"),
                _audit("open-hand-technique", "Open Hand Technique", "subclass"),
            ])
        if level >= 4:
            audits.append(_audit(
                "slow-fall", "Slow Fall", "class", combat=False, automated=False,
                notes="The standard Iron Pit arena has no falling hazard.",
            ))
        if level >= 5:
            audits.extend([
                _audit("extra-attack", "Extra Attack", "class"),
                _audit("stunning-strike", "Stunning Strike", "class"),
            ])
        if level >= 6:
            audits.extend([
                _audit("ki-empowered-strikes", "Ki-Empowered Strikes", "class"),
                _audit("wholeness-of-body", "Wholeness of Body", "subclass"),
            ])
        if level >= 7:
            audits.extend([
                _audit("evasion", "Evasion", "class"),
                _audit("stillness-of-mind", "Stillness of Mind", "class"),
            ])
        if level >= 10:
            audits.append(_audit("purity-of-body", "Purity of Body", "class"))
        return audits
    except Exception:
        logger.exception("Failed to compile 2014 Monk feature audits at level %s", level)
        raise

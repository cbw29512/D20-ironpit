from __future__ import annotations

import logging

from app.content.monk_open_hand_2014_audit_support import monk_feature_audit as _audit
from app.content.monk_open_hand_2014_endgame_audits import build_monk_2014_endgame_audits

logger = logging.getLogger(__name__)


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
                _audit(
                    "ki-empowered-strikes", "Ki-Empowered Strikes", "class",
                    notes="Level 6+ unarmed strikes carry the universal magical damage-source qualifier for conditional defenses.",
                ),
                _audit("wholeness-of-body", "Wholeness of Body", "subclass"),
            ])
        if level >= 7:
            audits.extend([
                _audit("evasion", "Evasion", "class"),
                _audit("stillness-of-mind", "Stillness of Mind", "class"),
            ])
        if level >= 10:
            audits.append(_audit("purity-of-body", "Purity of Body", "class"))
        if level >= 11:
            audits.append(_audit(
                "tranquility", "Tranquility", "subclass",
                notes=(
                    "Reuses the universal opening targeting-save gate with the Sanctuary timing: "
                    "Wisdom save to target Kael, ending when Kael attacks."
                ),
            ))
        if level >= 12:
            audits.append(_audit(
                "ability-score-improvement-l12", "Ability Score Improvement (+2 Wisdom)", "class",
                notes="Canonical progression raises Wisdom 15 to 17 and updates AC and Monk save DCs.",
            ))
        if level >= 13:
            audits.append(_audit(
                "tongue-of-the-sun-and-moon", "Tongue of the Sun and Moon", "class",
                combat=False, automated=False,
                notes="Language communication is arena-neutral and does not change combat resolution.",
            ))
        if level >= 14:
            audits.append(_audit(
                "diamond-soul", "Diamond Soul", "class",
                notes=(
                    "Reuses universal saving-throw proficiency grants plus a source-tagged "
                    "resource-backed failed-save reroll. The reroll preserves existing bonus dice."
                ),
            ))
        if level >= 15:
            audits.append(_audit(
                "timeless-body", "Timeless Body", "class",
                combat=False, automated=False,
                notes="Aging and food/water requirements do not change an Iron Pit duel.",
            ))
        if level >= 16:
            audits.append(_audit(
                "ability-score-improvement-l16", "Ability Score Improvement (+2 Wisdom)", "class",
                notes="Canonical progression raises Wisdom 17 to 19, updating AC, Wisdom saves, and Monk save DCs.",
            ))

        audits.extend(build_monk_2014_endgame_audits(level))

        return audits
    except Exception:
        logger.exception("Failed to compile 2014 Monk feature audits at level %s", level)
        raise

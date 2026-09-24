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
        source = "D&D SRD 5.1 (2014): School of Evocation" if category == "subclass" else "D&D SRD 5.1 (2014): Wizard"
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
        logger.exception("Failed to build 2014 Evoker audit for %s.", feature_id)
        raise


def build_wizard_evoker_2014_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit("light-crossbow", "Light Crossbow", "equipment", weapon_id="light-crossbow"),
            _audit(
                "wizard-spellcasting", "Spellcasting", "class", automated=False,
                notes="2014 spellbook and slot progression are prepared; the complete combat spell package is not yet bound.",
            ),
            _audit(
                "arcane-recovery", "Arcane Recovery", "class", combat=False, automated=False,
                notes="Recovery requires a short rest; Iron Pit has no in-fight short rest.",
            ),
        ]
        if level >= 2:
            audits.extend([
                _audit("evocation-savant", "Evocation Savant", "subclass", combat=False, automated=False),
                _audit(
                    "sculpt-spells", "Sculpt Spells", "subclass", combat=False, automated=False,
                    notes=(
                        "The standard Iron Pit ally-safe offensive AoE house rule already prevents friendly-team damage; "
                        "the source feature remains recorded but adds no separate arena outcome in that mode."
                    ),
                ),
            ])
        if level >= 6:
            audits.append(_audit(
                "potent-cantrip", "Potent Cantrip", "subclass",
                notes=(
                    "Poison Spray is a legal single-target Wizard save cantrip and reuses the generic "
                    "save-damage path with success_damage='half' from level 6 onward."
                ),
            ))
        if level >= 10:
            audits.append(_audit(
                "empowered-evocation", "Empowered Evocation", "subclass",
                notes="Uses the universal once-per-spell damage bonus grant for eligible Evocation spell IDs.",
            ))
        if level >= 14:
            audits.append(_audit(
                "overchannel", "Overchannel", "subclass", automated=False,
                notes="Requires reusable maximum spell-damage resolution plus repeated-use self-damage tracking.",
            ))
        if level >= 18:
            audits.append(_audit(
                "spell-mastery", "Spell Mastery", "class", automated=False,
                notes="Requires chosen 1st/2nd-level spells to cast without spending slots.",
            ))
        if level >= 20:
            audits.append(_audit(
                "signature-spells", "Signature Spells", "class", automated=False,
                notes="Requires prepared signature-spell state and once-per-rest free casting.",
            ))
        return audits
    except Exception:
        logger.exception("Failed to compile 2014 Evoker audits at level %s.", level)
        raise

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
        source = "D&D SRD 5.1 (2014): Circle of the Land" if category == "subclass" else "D&D SRD 5.1 (2014): Druid"
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
        logger.exception("Failed to build 2014 Land Druid audit for %s.", feature_id)
        raise


def build_druid_land_2014_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit("scimitar", "Scimitar", "equipment", weapon_id="scimitar"),
            _audit(
                "druid-spellcasting", "Spellcasting", "class", automated=False,
                notes="2014 slot progression is prepared; the complete combat spell package is not yet bound.",
            ),
            _audit("druidic", "Druidic", "class", combat=False, automated=False),
        ]
        if level >= 2:
            audits.extend([
                _audit(
                    "wild-shape", "Wild Shape", "class", automated=False,
                    notes=(
                        "Replacement-form state, legal 2014 beast-form filtering, HP replacement, action access, "
                        "movement modes, concentration, and revert lifecycle require the shared transformation engine."
                    ),
                ),
                _audit(
                    "natural-recovery", "Natural Recovery", "subclass", combat=False, automated=False,
                    notes="Recovery occurs during a short rest; Iron Pit has no in-fight short rest.",
                ),
                _audit("land-bonus-cantrip", "Bonus Cantrip", "subclass", automated=False),
            ])
        if level >= 3:
            audits.append(_audit(
                "land-circle-spells", "Circle Spells", "subclass", automated=False,
                notes="Circle spell choices remain part of the pending 2014 combat spell package.",
            ))
        if level >= 6:
            audits.append(_audit(
                "lands-stride", "Land's Stride", "subclass", automated=False,
                notes="Requires reusable difficult-terrain and magical-plant movement/save handling.",
            ))
        if level >= 10:
            audits.append(_audit(
                "natures-ward", "Nature's Ward", "subclass", automated=False,
                notes="Requires source-owned charm/fright immunity against elementals/fey plus poison/disease immunity.",
            ))
        if level >= 14:
            audits.append(_audit(
                "natures-sanctuary", "Nature's Sanctuary", "subclass", automated=False,
                notes="Requires source-creature-type-gated attack save/retarget behavior for beasts and plants.",
            ))
        if level >= 18:
            audits.extend([
                _audit("timeless-body", "Timeless Body", "class", combat=False, automated=False),
                _audit(
                    "beast-spells", "Beast Spells", "class", automated=False,
                    notes="Depends on shared Wild Shape replacement-form casting permissions.",
                ),
            ])
        if level >= 20:
            audits.append(_audit(
                "archdruid", "Archdruid", "class", automated=False,
                notes="Unlimited Wild Shape depends on the shared Wild Shape action/resource implementation.",
            ))
        return audits
    except Exception:
        logger.exception("Failed to compile 2014 Land Druid audits at level %s.", level)
        raise

from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def _audit(feature_id: str, name: str, category: str, *, combat: bool = True,
           automated: bool = True, weapon_id: str | None = None,
           notes: str | None = None) -> FeatureAudit:
    try:
        source = "D&D SRD 5.1 (2014): Draconic Bloodline" if category == "subclass" else "D&D SRD 5.1 (2014): Sorcerer"
        return FeatureAudit(
            feature_id=feature_id, feature_name=name, source_reference=source,
            category=category, combat_relevant=combat, automated=automated,
            runtime_attack_weapon_id=weapon_id, notes=notes,
        )
    except Exception:
        logger.exception("Failed to build 2014 Draconic Sorcerer audit for %s.", feature_id)
        raise


def build_sorcerer_draconic_2014_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit("light-crossbow", "Light Crossbow", "equipment", weapon_id="nyra-2014-light-crossbow"),
            _audit("sorcerer-spellcasting", "Spellcasting", "class", automated=False,
                   notes="2014 slots/spells-known are prepared; the combat spell package is not yet fully bound."),
            _audit("draconic-ancestry-red", "Dragon Ancestor (Red)", "subclass", combat=False, automated=False),
            _audit("draconic-resilience", "Draconic Resilience", "subclass",
                   notes="+1 maximum HP per Sorcerer level and unarmored AC 13 + Dexterity are compiled directly."),
        ]
        if level >= 2:
            audits.append(_audit("font-of-magic", "Font of Magic", "class", automated=False,
                                 notes="Sorcery Point resource exists; slot conversion is not yet automated."))
        if level >= 3:
            audits.append(_audit("metamagic", "Metamagic", "class", automated=False,
                                 notes="Requires source-neutral spell-parameter transforms before options are selected."))
        if level >= 6:
            audits.append(_audit("elemental-affinity", "Elemental Affinity", "subclass", automated=False,
                                 notes="The one-roll fire spell damage bonus is bound generically; resource-backed fire resistance activation remains pending."))
        if level >= 14:
            audits.append(_audit("dragon-wings", "Dragon Wings", "subclass", automated=False,
                                 notes="Needs generic bonus-action movement-mode activation; Pit flight remains horizontal."))
        if level >= 18:
            audits.append(_audit("draconic-presence", "Draconic Presence", "subclass", automated=False,
                                 notes="Needs generic timed hostile aura with start-turn save, condition choice, concentration, and immunity-on-success."))
        if level >= 20:
            audits.append(_audit("sorcerous-restoration", "Sorcerous Restoration", "class", combat=False, automated=False,
                                 notes="Short-rest recovery does not occur inside a standard Iron Pit fight."))
        return audits
    except Exception:
        logger.exception("Failed to compile Nyra's 2014 Sorcerer audits at level %s.", level)
        raise

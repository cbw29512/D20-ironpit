from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def _audit(feature_id: str, name: str, category: str, *, combat: bool = True,
           automated: bool = True, weapon_id: str | None = None,
           notes: str | None = None) -> FeatureAudit:
    try:
        source = "D&D SRD 5.1 (2014): Hunter" if category == "subclass" else "D&D SRD 5.1 (2014): Ranger"
        return FeatureAudit(
            feature_id=feature_id, feature_name=name, source_reference=source,
            category=category, combat_relevant=combat, automated=automated,
            runtime_attack_weapon_id=weapon_id, notes=notes,
        )
    except Exception:
        logger.exception("Failed to build 2014 Hunter Ranger audit for %s.", feature_id)
        raise


def build_ranger_hunter_2014_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit("longbow", "Longbow", "equipment", weapon_id="rowan-2014-longbow"),
            _audit("shortsword", "Shortsword", "equipment", weapon_id="rowan-2014-shortsword"),
            _audit("favored-enemy", "Favored Enemy", "class", combat=False, automated=False),
            _audit("natural-explorer", "Natural Explorer", "class", combat=False, automated=False),
        ]
        if level >= 2:
            audits.extend([
                _audit("archery", "Archery Fighting Style", "class"),
                _audit("ranger-spellcasting", "Spellcasting", "class", automated=False,
                       notes="2014 slots/spells-known are prepared; combat spell package and Hunter's Mark transfer are pending."),
            ])
        if level >= 3:
            audits.extend([
                _audit("primeval-awareness", "Primeval Awareness", "class", combat=False, automated=False),
                _audit("colossus-slayer", "Colossus Slayer", "subclass",
                       notes="Uses the generic once-per-turn weapon-hit rider with target-below-max-HP predicate."),
            ])
        if level >= 5:
            audits.append(_audit("extra-attack", "Extra Attack", "class"))
        if level >= 7:
            audits.append(_audit("multiattack-defense", "Multiattack Defense", "subclass", automated=False,
                                 notes="Needs a source-neutral subsequent-attacks-from-same-attacker AC modifier."))
        if level >= 8:
            audits.append(_audit("lands-stride", "Land's Stride", "class", automated=False,
                                 notes="Nonmagical difficult terrain bypass is already bound to the universal movement-defense grant; only the separate magical-plant movement/save clauses remain unbound."))
        if level >= 10:
            audits.append(_audit("hide-in-plain-sight", "Hide in Plain Sight", "class", automated=False,
                                 notes="Precombat camouflage/Stealth setup is not yet automated."))
        if level >= 11:
            audits.append(_audit("volley", "Volley", "subclass", automated=False,
                                 notes="Needs generic one-Attack-action multi-target weapon attack composition."))
        if level >= 14:
            audits.append(_audit("vanish", "Vanish", "class", automated=False,
                                 notes="Bonus-action Hide and tracking ribbon remain unbound."))
        if level >= 15:
            audits.append(_audit("evasion", "Evasion", "subclass",
                                 notes="Reuses the universal Dexterity-save Evasion primitive used by Rogue and Monk."))
        if level >= 18:
            audits.append(_audit("feral-senses", "Feral Senses", "class", automated=False,
                                 notes="Needs the universal visibility/nearby-invisible targeting audit completed."))
        if level >= 20:
            audits.append(_audit("foe-slayer", "Foe Slayer", "class", automated=False,
                                 notes="Needs favored-enemy-qualified once-per-turn attack-or-damage bonus choice."))
        return audits
    except Exception:
        logger.exception("Failed to compile Rowan's 2014 Ranger audits at level %s.", level)
        raise

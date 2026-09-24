from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def _audit(feature_id: str, name: str, category: str, *, combat: bool = True,
           automated: bool = True, weapon_id: str | None = None,
           notes: str | None = None) -> FeatureAudit:
    try:
        source = "D&D SRD 5.1 (2014): The Fiend" if category == "subclass" else "D&D SRD 5.1 (2014): Warlock"
        return FeatureAudit(
            feature_id=feature_id, feature_name=name, source_reference=source,
            category=category, combat_relevant=combat, automated=automated,
            runtime_attack_weapon_id=weapon_id, notes=notes,
        )
    except Exception:
        logger.exception("Failed to build 2014 Fiend Warlock audit for %s.", feature_id)
        raise


def build_warlock_fiend_2014_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit("light-crossbow", "Light Crossbow", "equipment", weapon_id="varek-2014-light-crossbow"),
            _audit("pact-magic", "Pact Magic", "class", automated=False,
                   notes="Pact slot count/level is prepared. Generic spell casting still needs mandatory higher-slot use for lower-level Warlock spells."),
            _audit("dark-ones-blessing", "Dark One's Blessing", "subclass",
                   notes="Uses the universal hostile-zero-HP Temporary HP reward trigger with the source-scaled amount stored in progression data."),
        ]
        if level >= 2:
            audits.append(_audit("eldritch-invocations", "Eldritch Invocations", "class", automated=False,
                                 notes="Canonical invocation package will bind only supported universal spell/attack modifiers."))
        if level >= 3:
            audits.append(_audit("pact-of-the-tome", "Pact of the Tome", "class", automated=False,
                                 notes="Additional cantrips are part of the pending spell package."))
        if level >= 6:
            audits.append(_audit("dark-ones-own-luck", "Dark One's Own Luck", "subclass",
                                 notes="Uses the generic resource-backed failed-D20 additive die on ability checks and saving throws."))
        if level >= 10:
            audits.append(_audit("fiendish-resilience", "Fiendish Resilience", "subclass", automated=False,
                                 notes="Needs source-qualified chosen resistance including magical/silver weapon bypass semantics."))
        if level >= 11:
            audits.append(_audit("mystic-arcanum", "Mystic Arcanum", "class", automated=False,
                                 notes="One-use arcanum resources are prepared; selected arcanum spell actions remain pending."))
        if level >= 14:
            audits.append(_audit("hurl-through-hell", "Hurl Through Hell", "subclass", automated=False,
                                 notes="Needs generic temporary removal/return plus delayed 10d10 psychic damage and Fiend exclusion."))
        if level >= 20:
            audits.append(_audit("eldritch-master", "Eldritch Master", "class", automated=False,
                                 notes="One-minute in-combat Pact slot recovery action is not yet automated."))
        return audits
    except Exception:
        logger.exception("Failed to compile Varek's 2014 Warlock audits at level %s.", level)
        raise

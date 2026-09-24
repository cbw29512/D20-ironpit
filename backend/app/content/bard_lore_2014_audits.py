from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def _audit(feature_id: str, name: str, category: str, *, combat: bool = True,
           automated: bool = True, weapon_id: str | None = None,
           notes: str | None = None) -> FeatureAudit:
    try:
        source = (
            "D&D SRD 5.1 (2014): College of Lore"
            if category == "subclass"
            else "D&D SRD 5.1 (2014): Bard / Half-Elf"
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
        logger.exception("Failed to build 2014 Lore Bard audit for %s", feature_id)
        raise


def build_bard_lore_2014_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit(
                "fey-ancestry", "Fey Ancestry", "species", automated=False,
                notes=(
                    "Charm-save Advantage maps to the universal contextual save-Advantage grant. "
                    "Magical sleep immunity remains unbound, so the complete feature is not certified."
                ),
            ),
            _audit("rapier", "Rapier", "equipment", weapon_id="lyra-2014-rapier"),
            _audit("bard-spellcasting", "Spellcasting", "class", automated=False,
                   notes="2014 slots/spells-known data is prepared; combat spell package is not yet fully bound."),
            _audit("bardic-inspiration", "Bardic Inspiration", "class", automated=False,
                   notes="Requires a universal resource-backed additive D20 bonus-die handoff."),
        ]
        if level >= 2:
            audits.extend([
                _audit("jack-of-all-trades", "Jack of All Trades", "class", automated=False,
                       notes="Prepared initiative half-proficiency is bound; generic nonproficient checks remain."),
                _audit("song-of-rest", "Song of Rest", "class", combat=False, automated=False,
                       notes="No short-rest healing occurs inside an Iron Pit fight."),
            ])
        if level >= 3:
            audits.extend([
                _audit("expertise", "Expertise", "class",
                       notes="Static selected-skill proficiency doubling is reflected in runtime bonuses."),
                _audit("lore-bonus-proficiencies", "Bonus Proficiencies", "subclass",
                       notes="Three additional Lore skill proficiencies are reflected in runtime bonuses."),
                _audit("cutting-words", "Cutting Words", "subclass", automated=False,
                       notes="Needs a universal reaction roll/damage reduction primitive using Bardic Inspiration."),
            ])
        if level >= 5:
            audits.append(_audit(
                "font-of-inspiration", "Font of Inspiration", "class", combat=False, automated=False,
                notes="Iron Pit resets resources between fights; in-fight short-rest recovery does not occur.",
            ))
        if level >= 6:
            audits.extend([
                _audit("countercharm", "Countercharm", "class", automated=False,
                       notes="Needs a timed 30-foot ally save-Advantage aura for charmed/frightened effects."),
                _audit("additional-magical-secrets", "Additional Magical Secrets", "subclass", automated=False,
                       notes="Spell choices will be selected from supported combat primitives."),
            ])
        if level >= 10:
            audits.append(_audit("magical-secrets", "Magical Secrets", "class", automated=False,
                                 notes="Spell choices remain part of the pending combat spell package."))
        if level >= 14:
            audits.append(_audit(
                "peerless-skill", "Peerless Skill", "subclass",
                notes=(
                    "Uses the generic resource-backed failed-D20 additive die on Lyra's own ability checks, "
                    "spending one Bardic Inspiration die of the current progression size."
                ),
            ))
        if level >= 20:
            audits.append(_audit(
                "superior-inspiration", "Superior Inspiration", "class",
                notes="Uses the universal initiative resource-refill grant when Bardic Inspiration is at zero.",
            ))
        return audits
    except Exception:
        logger.exception("Failed to compile 2014 Lore Bard audits at level %s", level)
        raise

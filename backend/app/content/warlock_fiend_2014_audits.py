from __future__ import annotations

import logging

from app.content.warlock_fiend_2014_high_audits import build_varek_fiend_2014_high_audits
from app.content.warlock_fiend_2014_low_audits import build_varek_fiend_2014_low_audits
from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def build_varek_fiend_2014_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = build_varek_fiend_2014_low_audits(level)
        if level >= 9:
            audits += [
                FeatureAudit(
                    feature_id="flame-strike", feature_name="Flame Strike",
                    source_reference="D&D Basic Rules 2014: The Fiend Expanded Spell List",
                    category="subclass", combat_relevant=True, automated=True,
                    notes="Reuses the universal multi-component area save-damage primitive.",
                ),
                FeatureAudit(
                    feature_id="whispers-of-the-grave", feature_name="Whispers of the Grave",
                    source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                    category="class", combat_relevant=False, automated=True,
                    notes="Arena-neutral utility invocation.",
                ),
            ]
        if level >= 10:
            audits.append(FeatureAudit(
                feature_id="fiendish-resilience", feature_name="Fiendish Resilience",
                source_reference="D&D Basic Rules 2014: The Fiend 10",
                category="subclass", combat_relevant=True, automated=True,
                notes="Uses the generic precombat best-resistance selector and conditional damage defense.",
            ))
        if level >= 11:
            audits += [
                FeatureAudit(
                    feature_id="eldritch-blast-third-beam", feature_name="Eldritch Blast — Three Beams",
                    source_reference="D&D Basic Rules 2014: Eldritch Blast",
                    category="class", combat_relevant=True, automated=True,
                    notes="Uses the universal multi-spell-attack sequence.",
                ),
                FeatureAudit(
                    feature_id="mystic-arcanum-6", feature_name="Mystic Arcanum (6th Level)",
                    source_reference="D&D Basic Rules 2014: Warlock 11",
                    category="class", combat_relevant=True, automated=True,
                    notes="Circle of Death uses a separate one-use resource and shared area-save primitive.",
                ),
            ]
        if level >= 12:
            audits += [
                FeatureAudit(
                    feature_id="ability-score-improvement-l12", feature_name="Ability Score Improvement",
                    source_reference="D&D Basic Rules 2014: Warlock 12",
                    category="class", combat_relevant=True, automated=True,
                    notes="Raises Constitution 14→16 through the certified build profile.",
                ),
                FeatureAudit(
                    feature_id="eyes-of-the-rune-keeper", feature_name="Eyes of the Rune Keeper",
                    source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                    category="class", combat_relevant=False, automated=True,
                    notes="Arena-neutral utility invocation.",
                ),
            ]
        if level >= 13:
            audits.append(FeatureAudit(
                feature_id="mystic-arcanum-7", feature_name="Mystic Arcanum (7th Level)",
                source_reference="D&D Basic Rules 2014: Warlock 13; Finger of Death",
                category="class", combat_relevant=True, automated=True,
                notes="Finger of Death uses universal resource-backed save damage; zombie creation is arena-inert.",
            ))
        if level >= 14:
            audits.append(FeatureAudit(
                feature_id="hurl-through-hell", feature_name="Hurl Through Hell",
                source_reference="D&D Basic Rules 2014: The Fiend 14",
                category="subclass", combat_relevant=True, automated=True,
                notes="Uses resource-backed on-hit exile, source-turn-end return, and conditional return damage.",
            ))
        audits.extend(build_varek_fiend_2014_high_audits(level))
        return audits
    except Exception:
        logger.exception("Failed to build Varek's 2014 Fiend audits at level %s.", level)
        raise

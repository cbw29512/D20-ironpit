from __future__ import annotations

import logging

from app.content.druid_2024_audit_support import druid_feature_audit
from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def build_druid_2024_final_progression_audits(level: int) -> list[FeatureAudit]:
    try:
        audits: list[FeatureAudit] = []
        if level >= 18:
            audits.extend([
                druid_feature_audit(
                    "beast-spells", "Beast Spells", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Reuses the universal replacement-form spell allowlist. In Wild Shape, "
                        "Thalen retains source-audited Druid spell actions whose Material component "
                        "has no specified cost and is not consumed; no Druid-specific spell resolver."
                    ),
                ),
                druid_feature_audit(
                    "druid-combat-spell-l18", "Prepared Spell: Barkskin", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "The twentieth prepared spell is explicit 2024 Barkskin: Bonus Action, Touch, "
                        "1 hour, no Concentration, and AC 17 when the target's AC would otherwise be lower, "
                        "through the universal minimum-AC modifier."
                    ),
                ),
            ])
        if level >= 19:
            audits.extend([
                druid_feature_audit(
                    "boon-of-fate", "Boon of Fate", "feat",
                    combat_relevant=True, automated=True,
                    notes=(
                        "The Druid Epic Boon feature permits any qualified Epic Boon. Thalen chooses "
                        "Boon of Fate for the established damage-caster build, gaining +1 Intelligence "
                        "and reusing the universal resource-backed 2d4 D20 outcome adjustment plus "
                        "initiative refill mechanics."
                    ),
                ),
                druid_feature_audit(
                    "druid-combat-spell-l19", "Prepared Spell: Regenerate", "class",
                    combat_relevant=False, automated=True,
                    notes=(
                        "The twenty-first prepared spell follows healing priority. Its 1-minute casting "
                        "time is not a legal normal-turn cast, and Foresight already occupies the one "
                        "arena-entry opening buff, so Arena AI never selects it in a standard match."
                    ),
                ),
            ])
        if level >= 20:
            audits.extend([
                druid_feature_audit(
                    "archdruid", "Archdruid", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Evergreen Wild Shape reuses initiative resource refill when Wild Shape is zero. "
                        "Nature Magician declares the four legal no-action Wild Shape exchanges for level "
                        "2/4/6/8 spell slots through universal resource conversion, gated once per Long Rest. "
                        "Longevity is arena-neutral."
                    ),
                ),
                druid_feature_audit(
                    "druid-combat-spell-l20", "Prepared Spell: Ice Storm", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "The twenty-second prepared spell follows damage priority. 2024 Ice Storm uses "
                        "the multi-component Dexterity-save path for 2d10 Bludgeoning plus 4d8 Cold, "
                        "half on a success, and places magical Difficult Terrain in the 20-foot cylinder "
                        "until the end of the caster's next turn."
                    ),
                ),
            ])
        return audits
    except Exception:
        logger.exception("Failed to build final 2024 Druid progression audits for level %s.", level)
        raise

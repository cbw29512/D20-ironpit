from __future__ import annotations

import logging

from app.content.paladin_devotion_2024_profile_support import paladin_2024_feature
from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def build_paladin_2024_high_feature_audits(level: int) -> list[FeatureAudit]:
    """Keep later source audits separate while sharing the cumulative build."""
    try:
        audits: list[FeatureAudit] = []
        if level >= 10:
            audits.append(paladin_2024_feature(
                "aura-of-courage",
                "Aura of Courage",
                "class",
                combat=True,
                automated=True,
                notes=("Reuses the universal friendly condition-immunity aura. "
                       "Aurelia and allies inside Aura of Protection are immune to Frightened; "
                       "an existing Frightened condition is suppressed while the creature remains "
                       "inside the aura, and the aura is inactive while Aurelia is Incapacitated."),
            ))
        if level >= 11:
            audits.extend([
                paladin_2024_feature(
                    "radiant-strikes",
                    "Radiant Strikes",
                    "class",
                    combat=True,
                    automated=True,
                    notes=("Reuses generic on-hit damage. Each qualifying Melee-weapon hit "
                           "adds 1d8 Radiant damage and doubles that damage die on a Critical Hit."),
                ),
            ])
        if level >= 12:
            audits.append(paladin_2024_feature(
                "ability-score-improvement-l12",
                "Ability Score Improvement (+2 Charisma)",
                "feat", combat=True, automated=True,
                notes=("Continue the persistent build: Charisma 15 to 17. Shared derived "
                       "values update saves, skills, healing, Sacred Weapon, Abjure Foes, "
                       "and Aura of Protection; no new combat primitive is required."),
            ))
        return audits
    except Exception:
        logger.exception("Failed to build later 2024 Paladin feature audits at level %s.", level)
        raise

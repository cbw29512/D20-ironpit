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
                           "adds 1d8 Radiant damage, including a thrown Melee weapon, "
                           "and doubles that damage die on a Critical Hit."),
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
        if level >= 13:
            audits.extend([
                paladin_2024_feature(
                    "oath-spells-level13", "Oath of Devotion Spells", "subclass",
                    combat=True, automated=True,
                    notes=("Freedom of Movement reuses the certified 2024 movement/debuff-counter "
                           "binding. Guardian of Faith remains always prepared in source metadata "
                           "and arena-unavailable under the no-summons contract."),
                ),
            ])
        if level >= 14:
            audits.append(paladin_2024_feature(
                "restoring-touch", "Restoring Touch", "class", combat=True, automated=True,
                notes=("Reuses the universal multi-condition removal action as one Bonus Action "
                       "Lay On Hands use. Each Blinded, Charmed, Deafened, Frightened, Paralyzed, "
                       "or Stunned condition costs five pool points; Poisoned can be removed "
                       "in the same use. Arena AI selects removal without optional HP healing."),
            ))
        if level >= 15:
            audits.append(paladin_2024_feature(
                "smite-of-protection", "Smite of Protection", "subclass",
                combat=True, automated=True,
                notes=("Divine Smite's generic post-hit damage may trigger a declared timed "
                       "source-centered friendly aura. For Smite of Protection that aura grants "
                       "Half Cover (+2 AC and +2 Dexterity saves) to Aurelia and allies inside "
                       "Aura of Protection until the start of Aurelia's next turn. Cover uses "
                       "the strongest cover source rather than stacking. No Paladin-specific resolver."),
            ))
        if level >= 16:
            audits.append(paladin_2024_feature(
                "ability-score-improvement-l16",
                "Ability Score Improvement (+2 Charisma)",
                "feat", combat=True, automated=True,
                notes=("Continue the persistent build: Charisma 17 to 19. Shared derived values "
                       "update Charisma saves and skills, healing, Sacred Weapon, Abjure Foes, "
                       "and Aura of Protection from +3 to +4; no new combat primitive is required."),
            ))
        if level >= 17:
            audits.append(paladin_2024_feature(
                "oath-spells-level17",
                "Oath of Devotion Spells",
                "subclass", combat=True, automated=True,
                notes=("Commune is arena-neutral. Flame Strike reuses the universal multi-component "
                       "Dexterity-save damage path with an explicit 2024 fingerprint: 5d6 Fire plus "
                       "5d6 Radiant on a failed save, half on a success."),
            ))
        if level >= 18:
            audits.append(paladin_2024_feature(
                "aura-expansion",
                "Aura Expansion",
                "class", combat=True, automated=True,
                notes=("Parameter-only delta on the existing universal friendly aura primitives. "
                       "Aura of Protection, Aura of Courage, Aura of Devotion, and the subclass's "
                       "Smite of Protection cover aura use a 30-foot radius at level 18. No new resolver."),
            ))
        if level >= 19:
            audits.extend([
                paladin_2024_feature(
                    "boon-combat-prowess",
                    "Boon of Combat Prowess",
                    "feat", combat=True, automated=True,
                    notes=("Aurelia raises Charisma 19 to 20. Peerless Aim reuses the universal "
                           "miss-to-hit override and start-of-turn one-use resource refill; no "
                           "Paladin-specific resolver is introduced."),
                ),
                paladin_2024_feature(
                    "banishing-smite",
                    "Banishing Smite",
                    "class", combat=False, automated=False,
                    notes=("Selected as the fifteenth damage-first Paladin preparation. It remains "
                           "fail-closed until the shared post-hit Concentration and banishment semantics "
                           "are fully represented; no approximation is allowed."),
                ),
            ])
        if level >= 20:
            audits.append(paladin_2024_feature(
                "holy-nimbus",
                "Holy Nimbus",
                "subclass", combat=True, automated=True,
                notes=("Composes existing universal mechanics: a Bonus Action finite timed self-buff; "
                       "all-save Advantage against Fiend/Undead sources; 30-foot enemy-turn-start "
                       "Radiant damage equal to Charisma modifier plus Proficiency Bonus; a 30-foot "
                       "sunlight environment-context aura consumed by target-owned traits; and a "
                       "no-action level-5-slot resource conversion that restores the finite use. "
                       "Aura effects pause while Aura of Protection is inactive from Incapacitated "
                       "without ending the 10-minute duration. No Paladin or monster-name resolver."),
            ))
        return audits
    except Exception:
        logger.exception("Failed to build later 2024 Paladin feature audits at level %s.", level)
        raise

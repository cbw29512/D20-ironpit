from __future__ import annotations

import logging

from app.content.paladin_devotion_2024_feature_audits_high import build_paladin_2024_high_feature_audits
from app.content.paladin_devotion_2024_profile_support import paladin_2024_feature
from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)

def _level_five() -> list[FeatureAudit]:
    return [
        paladin_2024_feature("extra-attack", "Extra Attack", "class", combat=True, automated=True,
                             notes="The universal Attack action resolves two legal weapon attacks."),
        paladin_2024_feature(
            "faithful-steed", "Faithful Steed", "class", combat=False, automated=False,
            notes=("Find Steed is always prepared and retains its one free Long-Rest cast resource, "
                   "but Iron Pit's no-summons rule keeps the summon arena-unavailable."),
        ),
        paladin_2024_feature(
            "oath-spells-level5", "Oath of Devotion Spells", "subclass",
            combat=True, automated=True,
            notes=("Aid uses the certified 2024 defensive-spell fingerprint; "
                   "Zone of Truth is always prepared but arena-neutral."),
        ),
    ]


def _level_six() -> list[FeatureAudit]:
    return [paladin_2024_feature(
        "aura-of-protection", "Aura of Protection", "class", combat=True, automated=True,
        notes=("Universal friendly saving-throw aura: 10-foot Emanation, "
               "Charisma-modifier flat save bonus, inactive while the source is Incapacitated."),
    )]


def _level_seven() -> list[FeatureAudit]:
    return [
        paladin_2024_feature(
            "aura-of-devotion", "Aura of Devotion", "subclass", combat=True, automated=True,
            notes=("Universal friendly condition-immunity aura: Charmed immunity inside "
                   "Aura of Protection's 10-foot Emanation, inactive while the source is Incapacitated."),
        ),
        paladin_2024_feature(
            "lesser-restoration", "Lesser Restoration", "class", combat=True, automated=True,
            notes=("Seventh ordinary preparation reuses the certified 2024 universal "
                   "condition-removal action."),
        ),
    ]


def _level_nine() -> list[FeatureAudit]:
    return [
        paladin_2024_feature(
            "abjure-foes", "Abjure Foes", "class", combat=True, automated=True,
            notes=("One Channel Divinity powers a universal capped multi-target Wisdom-save action. "
                   "Failed targets are Frightened for up to 1 minute or until damaged and may choose "
                   "only movement, an Action, or a Bonus Action on each affected turn."),
        ),
        paladin_2024_feature(
            "oath-spells-level9", "Oath of Devotion Spells", "subclass",
            combat=True, automated=True,
            notes=("Beacon of Hope uses explicit 2024 save/healing-maximization modifiers; "
                   "Dispel Magic uses the universal spell-effect removal action with Charisma."),
        ),
    ]


def build_paladin_2024_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            paladin_2024_feature("lay-on-hands", "Lay On Hands", "class", combat=True, automated=True),
            paladin_2024_feature(
                "spellcasting", "Spellcasting", "class", combat=True, automated=True,
                notes=("Damage/healing-first preparation uses Cure Wounds and Divine Favor; "
                       "level 2 adds certified Bless while Divine Smite is always prepared separately."),
            ),
            paladin_2024_feature("weapon-mastery", "Weapon Mastery", "class", combat=True, automated=True,
                                 notes="Longsword uses Sap; Javelin uses Slow."),
            paladin_2024_feature("resourceful", "Resourceful", "species", combat=True, automated=True),
            paladin_2024_feature("skillful", "Skillful", "species", combat=False, automated=False),
            paladin_2024_feature("versatile-skilled", "Versatile: Skilled", "species", combat=False, automated=False),
            paladin_2024_feature("savage-attacker", "Savage Attacker", "feat", combat=True, automated=True),
            paladin_2024_feature("chain-mail", "Chain Mail", "equipment", combat=True, automated=True),
            paladin_2024_feature("shield", "Shield", "equipment", combat=True, automated=True),
            paladin_2024_feature("longsword", "Longsword", "equipment", combat=True, automated=True, weapon_id="longsword"),
            paladin_2024_feature("javelin", "Javelin", "equipment", combat=True, automated=True, weapon_id="javelin"),
        ]
        if level >= 2:
            audits.extend([
                paladin_2024_feature("fighting-style-defense", "Defense", "class", combat=True, automated=True,
                                     notes="Fighting Style feat grants +1 AC while Aurelia wears Chain Mail."),
                paladin_2024_feature(
                    "paladins-smite", "Paladin's Smite", "class", combat=True, automated=True,
                    notes=("Divine Smite is always prepared and has one Long-Rest free cast. "
                           "Its damage joins the triggering attack's damage roll."),
                ),
            ])
        if level >= 3:
            audits.extend([
                paladin_2024_feature("channel-divinity", "Channel Divinity", "class", combat=True, automated=True,
                                     notes=("Three" if level >= 11 else "Two") + " source-owned uses feed universal Channel Divinity consumers."),
                paladin_2024_feature(
                    "divine-sense", "Divine Sense", "class", combat=False, automated=False,
                    notes=("Arena state already exposes combatant creature type and position; "
                           "the detection feature does not change a current Iron Pit combat outcome."),
                ),
                paladin_2024_feature(
                    "sacred-weapon", "Sacred Weapon", "subclass", combat=True, automated=True,
                    notes=("Taking the Attack action spends one Channel Divinity to bind a 10-minute "
                           "weapon-scoped Charisma attack bonus and Radiant damage-type choice through "
                           "the universal Attack-action weapon-buff primitive."),
                ),
                paladin_2024_feature(
                    "oath-spells-level3", "Oath of Devotion Spells", "subclass", combat=True, automated=True,
                    notes=("Protection from Evil and Good and Shield of Faith are always prepared with "
                           "explicit 2024 modifier fingerprints."),
                ),
            ])
        if level >= 4:
            audits.append(paladin_2024_feature(
                "ability-score-improvement-l4", "Ability Score Improvement (+2 Strength)", "feat",
                combat=True, automated=True,
                notes=("Canonical sword-and-shield progression raises Strength 17 to 19; "
                       "shared derived-stat logic updates weapon attack/damage and Athletics."),
            ))
        if level >= 5:
            audits.extend(_level_five())
        if level >= 6:
            audits.extend(_level_six())
        if level >= 7:
            audits.extend(_level_seven())
        if level >= 8:
            audits.append(paladin_2024_feature(
                "ability-score-improvement-l8",
                "Ability Score Improvement (+1 Strength, +1 Charisma)",
                "feat",
                combat=True,
                automated=True,
                notes=("Canonical sword-and-shield progression caps Strength 19 to 20 and "
                       "raises Charisma 14 to 15; shared derived-stat logic updates weapon "
                       "attack/damage, Athletics, Charisma skills, spellcasting, and aura bonus."),
            ))
        if level >= 9:
            audits.extend(_level_nine())
        audits.extend(build_paladin_2024_high_feature_audits(level))
        return audits
    except Exception:
        logger.exception("Failed to build 2024 Paladin feature audits at level %s.", level)
        raise

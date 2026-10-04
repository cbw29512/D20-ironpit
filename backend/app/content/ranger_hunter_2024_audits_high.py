from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def _audit(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    combat: bool,
    automated: bool,
    notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_name,
        source_reference="D&D Beyond Basic Rules 2024",
        category=category,
        combat_relevant=combat,
        automated=automated,
        notes=notes,
    )


def ranger_2024_high_audits(level: int) -> list[FeatureAudit]:
    audits: list[FeatureAudit] = []
    if level >= 4:
        audits.append(_audit("ability-score-improvement", "Ability Score Improvement", "feat",
                             combat=True, automated=True, notes="Cumulative Dexterity and Wisdom increases."))
    if level >= 5:
        audits += [
            _audit("extra-attack", "Extra Attack", "class", combat=True, automated=True),
            _audit("lesser-restoration", "Lesser Restoration", "class", combat=True, automated=True),
        ]
    if level >= 6:
        audits.append(_audit("roving", "Roving", "class", combat=True, automated=True,
                             notes="+10 Speed while not in Heavy armor; Climb and Swim equal Speed."))
    if level >= 7:
        audits.append(_audit("defensive-tactics", "Defensive Tactics — Escape the Horde", "subclass",
                             combat=True, automated=True,
                             notes="Opportunity Attacks against Rowan have Disadvantage."))
    if level >= 9:
        audits += [
            _audit("expertise", "Expertise", "class", combat=True, automated=True,
                   notes="Expertise in Stealth and Survival."),
            _audit("dispel-magic", "Dispel Magic", "class", combat=True, automated=True,
                   notes="Action, 120 feet, Wisdom, auto-remove effects of level 3 or lower."),
        ]
    if level >= 10:
        audits.append(_audit("tireless", "Tireless", "class", combat=True, automated=True,
                             notes="Magic action Temporary HP 1d8+WIS, WIS-mod uses. Exhaustion decrease is between fights."))
    if level >= 11:
        audits.append(_audit("superior-hunters-prey", "Superior Hunter's Prey", "subclass",
                             combat=True, automated=True,
                             notes="Once per turn splash Hunter's Mark Force damage to a second creature within 30 feet."))
    if level >= 13:
        audits += [
            _audit("relentless-hunter", "Relentless Hunter", "class", combat=True, automated=True,
                   notes="Damage cannot break Concentration on Hunter's Mark."),
            _audit("freedom-of-movement", "Freedom of Movement", "class", combat=True, automated=True),
        ]
    if level >= 14:
        audits.append(_audit("natures-veil", "Nature's Veil", "class", combat=True, automated=True,
                             notes="Bonus Action Invisible until the end of the next turn, WIS-mod uses."))
    if level >= 15:
        audits.append(_audit("superior-hunters-defense", "Superior Hunter's Defense", "subclass",
                             combat=True, automated=True,
                             notes="Reaction Resistance to the triggering damage type until the end of the turn."))
    if level >= 17:
        audits.append(_audit("precise-hunter", "Precise Hunter", "class", combat=True, automated=True,
                             notes="Advantage on attacks against the creature marked by Hunter's Mark."))
    if level >= 18:
        audits.append(_audit("feral-senses", "Feral Senses", "class", combat=True, automated=True,
                             notes="Blindsight 30 feet."))
    if level >= 19:
        audits.append(_audit("ranger-epic-boon", "Boon of Combat Prowess", "feat", combat=True, automated=True,
                             notes="Recommended Dimensional Travel is a pit teleport ban. Combat Prowess is the legal martial boon."))
    if level >= 20:
        audits.append(_audit("foe-slayer", "Foe Slayer", "class", combat=True, automated=True,
                             notes="Hunter's Mark damage die becomes a d10."))
    return audits

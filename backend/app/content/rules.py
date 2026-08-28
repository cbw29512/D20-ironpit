from __future__ import annotations

import logging

from app.domain.rules import RuleCoverageEntry, RuleCoverageStatus, RulesCoverageReport

logger = logging.getLogger(__name__)
I = RuleCoverageStatus.IMPLEMENTED
P = RuleCoverageStatus.PARTIAL
U = RuleCoverageStatus.UNSUPPORTED
A = RuleCoverageStatus.ARENA_ASSUMPTION
SRC = {
    "init": "D&D Beyond Basic Rules (2024): Playing the Game — Combat — Initiative",
    "surprise": "D&D Beyond Basic Rules (2024): Rules Glossary — Surprise",
    "hide": "D&D Beyond Basic Rules (2024): Rules Glossary — Hide [Action]",
    "rogue": "D&D Beyond Basic Rules (2024): Character Classes — Rogue — Level 1: Sneak Attack",
    "attack": "D&D Beyond Basic Rules (2024): Playing the Game — Combat — Making an Attack",
    "crit": "D&D Beyond Basic Rules (2024): Playing the Game — Damage and Healing — Critical Hits",
    "adv": "D&D Beyond Basic Rules (2024): Rules Glossary — Advantage / Disadvantage",
    "range": "D&D Beyond Basic Rules (2024): Playing the Game — Combat — Ranged Attacks in Close Combat; Equipment — Weapon Range",
    "move": "D&D Beyond Basic Rules (2024): Playing the Game — Combat — Movement and Position",
    "dash": "D&D Beyond Basic Rules (2024): Rules Glossary — Dash [Action]",
    "hp": "D&D Beyond Basic Rules (2024): Playing the Game — Damage and Healing — Dropping to 0 Hit Points",
    "fighter": "D&D Beyond Basic Rules (2024): Character Classes — Fighter — Level 1: Second Wind",
    "light": "D&D Beyond Basic Rules (2024): Equipment — Weapon Properties — Light",
    "twf": "D&D Beyond Basic Rules (2024): Feats — Fighting Style Feats — Two-Weapon Fighting",
    "nick": "D&D Beyond Basic Rules (2024): Equipment — Mastery Properties — Nick",
    "sap": "D&D Beyond Basic Rules (2024): Equipment — Mastery Properties — Sap",
    "vex": "D&D Beyond Basic Rules (2024): Equipment — Mastery Properties — Vex",
    "goblin": "D&D Beyond Basic Rules (2024): Creature Stat Blocks — Goblin Warrior",
    "oa": "D&D Beyond Basic Rules (2024): Rules Glossary — Opportunity Attack",
    "disengage": "D&D Beyond Basic Rules (2024): Rules Glossary — Disengage [Action]",
    "reaction": "D&D Beyond Basic Rules (2024): Rules Glossary — Reaction",
    "nimble": "D&D Beyond Basic Rules (2024): Creature Stat Blocks — Goblin Warrior — Nimble Escape",
    "search": "D&D Beyond Basic Rules (2024): Rules Glossary — Search [Action]",
    "invisible": "D&D Beyond Basic Rules (2024): Rules Glossary — Invisible [Condition]",
    "incapacitated": "D&D Beyond Basic Rules (2024): Rules Glossary — Incapacitated [Condition]",
    "conditions": "D&D Beyond Basic Rules (2024): Playing the Game — Conditions; Rules Glossary",
    "cover": "D&D Beyond Basic Rules (2024): Playing the Game — Combat — Cover",
    "spells": "D&D Beyond Basic Rules (2024): Spells — Casting Spells",
    "death": "D&D Beyond Basic Rules (2024): Playing the Game — Damage and Healing — Death Saving Throws",
    "arena": "Iron Pit arena contract — explicit non-SRD assumption",
}


def _entry(id_: str, name: str, status: RuleCoverageStatus, notes: str, *sources: str) -> RuleCoverageEntry:
    return RuleCoverageEntry(id=id_, name=name, status=status, notes=notes, sources=[SRC[key] for key in sources])


def build_rules_coverage() -> RulesCoverageReport:
    try:
        entries = [
            _entry("initiative", "Initiative", P, "Core Initiative rolls plus Invisible Advantage and Surprise/Incapacitated Disadvantage are implemented; other condition/test modifiers and RAW tie adjudication are not complete.", "init", "incapacitated"),
            _entry("surprise", "Surprise", I, "Surprise imposes Disadvantage on Initiative; the engine does not invent a surprise round or free pre-Initiative attack.", "surprise", "init"),
            _entry("precombat-hide", "Pre-combat Hide", I, "Eligible scenario actors can attempt Hide before Initiative without spending their first combat Action or Bonus Action; failure does not create Surprise.", "hide", "init"),
            _entry("rogue-ambush", "Rogue ambush demo", I, "The scenario supplies valid concealment and an unaware target; the Hide check still determines whether the hidden opening and Surprise are earned.", "hide", "surprise", "rogue"),
            _entry("sneak-attack", "Rogue Sneak Attack", P, "Advantage route, Finesse/Ranged gating, once-per-turn timing including reaction turns, critical dice, and weapon damage type are implemented; the ally-within-5-feet route awaits ally-position context.", "rogue", "incapacitated"),
            _entry("attack-rolls", "Weapon attack rolls", I, "Base AC resolution, natural 1 misses, natural 20 hits, and supported attack modifiers are implemented.", "attack"),
            _entry("critical-hits", "Weapon critical hits", I, "Natural-20 attack criticals double the attack's eligible damage dice, including Sneak Attack and conditional attack damage, while modifiers are not doubled.", "crit"),
            _entry("advantage", "Advantage and Disadvantage", I, "Multiple Advantage or Disadvantage sources do not stack, and any amount of both cancels to a normal d20 roll.", "adv"),
            _entry("range", "Weapon range", P, "Melee reach, normal/long range, sight-dependent close-ranged Disadvantage, and the Incapacitated close-enemy exception are implemented; special-sense visibility remains incomplete.", "range", "invisible", "incapacitated"),
            _entry("movement", "Arena movement", A, "The arena tracks one-dimensional distance, Speed, closing, retreating, and remaining movement; it is not a general grid/terrain movement implementation.", "move", "arena"),
            _entry("dash", "Dash", I, "Dash spends the Action and grants extra movement equal to Speed within the current movement model; Incapacitated creatures are barred from taking it.", "dash", "move", "incapacitated"),
            _entry("hp-defeat", "0 HP arena defeat", A, "Damage and healing are tracked, but the duel treats 0 HP as defeat instead of running the full player-character death/unconsciousness rules.", "hp", "death", "arena"),
            _entry("second-wind", "Fighter Second Wind", P, "Bonus Action use, two level-1 uses, 1d10 + Fighter level healing, max-HP cap, and Incapacitated gating are implemented; Short/Long Rest recharge is not yet modeled.", "fighter", "incapacitated"),
            _entry("light-weapons", "Light weapon extra attack", I, "A Light-weapon Attack-action attack can enable one extra attack with a different Light weapon; Bonus Action cost, once-per-turn use, and ability-modifier damage restrictions are implemented.", "light"),
            _entry("two-weapon-fighting", "Two-Weapon Fighting style", I, "The Fighting Style restores the ability modifier to damage for the Light-property extra attack.", "twf", "light"),
            _entry("nick", "Nick mastery", I, "A mastered Nick weapon can move the one Light-property extra attack into the Attack action instead of spending the Bonus Action; it does not create another Light attack.", "nick", "light"),
            _entry("sap", "Sap mastery", I, "A mastered Sap weapon imposes Disadvantage on the target's next attack roll before the start of the wielder's next turn.", "sap"),
            _entry("vex", "Vex mastery", I, "A mastered Vex weapon that deals damage grants target-specific Advantage on the wielder's next attack against that creature before the end of the wielder's next turn, including reaction-applied timing.", "vex"),
            _entry("goblin-advantage-damage", "Goblin Advantage damage", I, "The Goblin Warrior's extra 1d4 damage applies only when that attack roll actually had Advantage.", "goblin"),
            _entry("opportunity-attacks", "Opportunity Attacks", P, "Reaction timing, pre-movement resolution, reach exit, Disengage suppression, current sight checks, and Incapacitated reaction gating are implemented; special-sense visibility and broader movement modes remain incomplete.", "oa", "disengage", "invisible", "incapacitated"),
            _entry("disengage", "Disengage", I, "The standard Disengage Action and Nimble Escape's Bonus Action reuse one resolver; the effect suppresses Opportunity Attacks from the creature's movement for the rest of the current turn.", "disengage", "oa", "nimble"),
            _entry("reactions", "Reactions", P, "Reaction availability, Incapacitated gating, and Opportunity Attacks are implemented; the broader Reaction rule space is not.", "reaction", "oa", "incapacitated"),
            _entry("nimble-escape", "Goblin Nimble Escape", P, "Bonus Action Disengage and Hide are both wired through canonical action resolvers; the Hide option inherits the partial Hide/Invisible visibility boundary.", "nimble", "hide", "disengage"),
            _entry("hide", "Hide", P, "DC 15 Stealth, supported concealment/line-of-sight eligibility, stored discovery DC, Search discovery, attack-roll reveal, pre-combat Hide, and Incapacitated gating are implemented; noise, Verbal-spell, and broader visibility/sense interactions remain incomplete.", "hide", "invisible", "incapacitated"),
            _entry("search-hidden", "Search for hidden creatures", I, "Wisdom (Perception) can use the Search action against a hidden creature's recorded Hide DC in the supported stealth model; Incapacitated creatures cannot take the action.", "search", "hide", "incapacitated"),
            _entry("invisible", "Invisible condition", P, "Initiative Advantage, concealed-state attack Advantage/Disadvantage, and supported sight checks are implemented; special senses and all seen-target effect restrictions are not.", "invisible"),
            _entry("incapacitated", "Incapacitated condition", P, "Action, Bonus Action, and Reaction prohibition plus Initiative Disadvantage are implemented without incorrectly removing normal movement; Concentration loss and speech prohibition await those systems.", "incapacitated", "conditions"),
            _entry("conditions", "Conditions", P, "Invisible and the combat-relevant Incapacitated subset are represented; the general condition framework is incomplete.", "conditions", "invisible", "incapacitated"),
            _entry("cover", "Cover", P, "Cover categories are represented for Hide eligibility; AC bonuses, Dexterity-save bonuses, and full line-of-effect behavior are not implemented.", "cover", "hide"),
            _entry("spells", "Spells", U, "Spellcasting is outside the current duel slice.", "spells"),
            _entry("death-saves", "Death Saving Throws", U, "Death Saving Throws and the complete 0-HP player-character flow are not implemented.", "death"),
            _entry("initiative-ties", "Initiative ties", A, "The arena currently uses Initiative bonus as a deterministic tiebreaker instead of the RAW player/DM tie decision process.", "init", "arena"),
            _entry("arena-geometry", "Arena geometry", A, "Combat uses one-dimensional distance with open-arena visibility by default and explicit per-actor concealment overrides.", "move", "arena"),
        ]
        return RulesCoverageReport(entries=entries)
    except Exception as exc:
        logger.exception("Failed to build rules coverage report.")
        raise RuntimeError("Rules coverage report could not be created.") from exc

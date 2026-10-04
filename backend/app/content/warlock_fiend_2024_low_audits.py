from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def _audit(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    combat_relevant: bool,
    automated: bool,
    runtime_attack_weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_name,
        source_reference="D&D Beyond Basic Rules 2024",
        category=category,
        combat_relevant=combat_relevant,
        automated=automated,
        runtime_attack_weapon_id=runtime_attack_weapon_id,
        notes=notes,
    )


def build_varek_fiend_2024_low_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit("human", "Human", "species", combat_relevant=True, automated=True,
                   notes="2024 Human supplies Resourceful, Skillful, and Versatile."),
            _audit("resourceful", "Resourceful", "species", combat_relevant=True, automated=True,
                   notes="Fresh-rest arena initialization starts Varek with Heroic Inspiration."),
            _audit("skillful", "Skillful", "species", combat_relevant=False, automated=True,
                   notes="Canonical extra skill is Deception."),
            _audit("versatile", "Versatile", "species", combat_relevant=False, automated=True,
                   notes="Recommended Skilled Origin feat selected."),
            _audit("skilled", "Skilled", "feat", combat_relevant=False, automated=True,
                   notes="Persuasion, Investigation, and Intimidation proficiencies selected."),
            _audit(
                "magic-initiate-cleric", "Magic Initiate (Cleric)", "feat",
                combat_relevant=False, automated=False,
                notes="Acolyte origin feat. Canonical Cleric choices stay arena-neutral.",
            ),
            _audit(
                "dagger", "Dagger", "equipment", combat_relevant=True, automated=True,
                runtime_attack_weapon_id="dagger",
                notes="2024 starting dagger is the mundane fallback; Warlock has no Weapon Mastery.",
            ),
            _audit("pact-magic", "Pact Magic", "class", combat_relevant=True, automated=True,
                   notes="Prepared Pact Magic uses one shared slot level that recovers on a Short or Long Rest."),
            _audit("eldritch-blast", "Eldritch Blast", "class", combat_relevant=True, automated=True,
                   notes="Uses the universal ranged spell-attack and force-damage primitives."),
            _audit("hex", "Hex", "class", combat_relevant=True, automated=True,
                   notes="2024 Hex durations are 1/4/8/8/24 hours by Pact slot level."),
            _audit("charm-person", "Charm Person", "class", combat_relevant=True, automated=True,
                   notes="2024 Charm Person is not Concentration; extra target per slot above 1; save Advantage if you or allies are fighting the target."),
            _audit("pact-of-the-tome", "Pact of the Tome", "class", combat_relevant=False, automated=True,
                   notes="Level 1 invocation. Bonus utility cantrips remain progression metadata."),
        ]
        if level >= 2:
            audits += [
                _audit("magical-cunning", "Magical Cunning", "class", combat_relevant=True, automated=True,
                       notes="1-minute DelayedResourceRefill restores half of maximum Pact slots, rounded up."),
                _audit("agonizing-blast", "Agonizing Blast", "class", combat_relevant=True, automated=True,
                       notes="Adds Charisma modifier to each certified Eldritch Blast beam."),
                _audit("eldritch-spear", "Eldritch Spear", "class", combat_relevant=True, automated=True,
                       notes="Adds 30 feet to Eldritch Blast range per Warlock level."),
            ]
        if level >= 3:
            audits += [
                _audit("fiend-patron", "Fiend Patron", "subclass", combat_relevant=True, automated=True,
                       notes="2024 patron begins at level 3 and always prepares its Fiend spells."),
                _audit("dark-ones-blessing", "Dark One's Blessing", "subclass", combat_relevant=True, automated=True,
                       notes="Temp HP on a source kill, and when someone else kills a hostile within 10 feet."),
                _audit("command", "Command", "subclass", combat_relevant=True, automated=True,
                       notes="Always-prepared Fiend spell. Arena binds Grovel: Prone plus the target's next turn ends."),
                _audit("suggestion", "Suggestion", "subclass", combat_relevant=True, automated=True,
                       notes="Always-prepared Fiend spell. Charmed stop-fighting suggestion ends if you or allies damage the target."),
            ]
        if level >= 4:
            audits.append(_audit(
                "ability-score-improvement-l4", "Ability Score Improvement", "class",
                combat_relevant=True, automated=True,
                notes="Raises Charisma 17→19 through the certified build profile.",
            ))
        if level >= 5:
            audits += [
                _audit(
                    "eldritch-blast-second-beam", "Eldritch Blast — Two Beams", "class",
                    combat_relevant=True, automated=True,
                    notes="Uses the universal multi-spell-attack sequence.",
                ),
                _audit("hold-person", "Hold Person", "class", combat_relevant=True, automated=True,
                       notes="Runtime Wisdom-save Paralyze from level 5, extra Humanoid per slot above 2."),
                _audit("stinking-cloud", "Stinking Cloud", "subclass", combat_relevant=True, automated=True,
                       notes="Always-prepared Fiend save zone: start-of-turn Con save or Poisoned with no Action or Bonus Action."),
            ]
        if level >= 6:
            audits += [
                _audit("dark-ones-own-luck", "Dark One's Own Luck", "subclass", combat_relevant=True, automated=True,
                       notes="Resource-backed d10 uses equal the Charisma modifier (minimum 1)."),
                _audit("dispel-magic", "Dispel Magic", "class", combat_relevant=True, automated=True,
                       notes="Reuses the universal effect-removal action."),
            ]
        if level >= 7:
            audits += [
                _audit("fire-shield", "Fire Shield", "subclass", combat_relevant=True, automated=True,
                       notes="Always-prepared Fiend buff: Cold or Fire resistance plus 2d8 melee-hit retaliation."),
                _audit("wall-of-fire", "Wall of Fire", "subclass", combat_relevant=True, automated=True,
                       notes="Always-prepared Fiend ringed wall: Dex 5d8 Fire half on appear, enter, and end turn."),
            ]
        if level >= 8:
            audits.append(_audit(
                "ability-score-improvement-l8", "Ability Score Improvement", "class",
                combat_relevant=True, automated=True,
                notes="Raises Charisma 19→20 and Wisdom 15→16 through the certified build profile.",
            ))
        return audits
    except Exception:
        logger.exception("Failed to build Varek's low-level 2024 Fiend audits at level %s.", level)
        raise

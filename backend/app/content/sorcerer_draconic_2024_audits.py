from __future__ import annotations

import logging

from app.content.sorcerer_draconic_2024_high_audits import build_nyra_2024_high_audits
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


def build_nyra_draconic_2024_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit("human", "Human", "species", combat_relevant=True, automated=True,
                   notes="2024 Human supplies Resourceful, Skillful, and Versatile."),
            _audit("resourceful", "Resourceful", "species", combat_relevant=True, automated=True,
                   notes="Fresh-rest arena initialization starts Nyra with Heroic Inspiration."),
            _audit("skillful", "Skillful", "species", combat_relevant=False, automated=True,
                   notes="Canonical extra skill is Deception."),
            _audit("versatile", "Versatile", "species", combat_relevant=False, automated=True,
                   notes="Recommended Skilled Origin feat selected."),
            _audit("skilled", "Skilled", "feat", combat_relevant=False, automated=True,
                   notes="Intimidation, Investigation, and History proficiencies selected."),
            _audit(
                "magic-initiate-cleric", "Magic Initiate (Cleric)", "feat",
                combat_relevant=False, automated=False,
                notes="Acolyte origin feat. Canonical Cleric choices stay arena-neutral.",
            ),
            _audit(
                "dagger", "Dagger", "equipment", combat_relevant=True, automated=True,
                runtime_attack_weapon_id="dagger",
                notes="2024 starting dagger is the mundane fallback; Sorcerer has no Weapon Mastery.",
            ),
            _audit("spellcasting", "Spellcasting", "class", combat_relevant=True, automated=True,
                   notes="Prepared Sorcerer spells use Charisma and the full-caster slot table."),
            _audit("innate-sorcery", "Innate Sorcery", "class", combat_relevant=True, automated=True,
                   notes="Bonus Action, 1 minute, +1 Sorcerer spell save DC and Advantage on Sorcerer spell attacks, 2/Long Rest."),
            _audit("fire-bolt", "Fire Bolt", "class", combat_relevant=True, automated=True,
                   notes="Uses the universal 2024 Fire Bolt fingerprint."),
            _audit("burning-hands", "Burning Hands", "class", combat_relevant=True, automated=True,
                   notes="Uses the universal 2024 Burning Hands fingerprint."),
            _audit("magic-missile", "Magic Missile", "class", combat_relevant=True, automated=True,
                   notes="Three 1d4+1 Force darts; one extra dart per slot above 1."),
        ]
        if level >= 2:
            audits += [
                _audit("font-of-magic", "Font of Magic", "class", combat_relevant=True, automated=True,
                       notes="Sorcery Points equal Sorcerer level. Creating a slot is a Bonus Action; converting a slot is no action."),
                _audit("heightened-spell", "Metamagic: Heightened Spell", "class", combat_relevant=True, automated=True,
                       notes="Spends 2 Sorcery Points to give one target Disadvantage on the spell's save."),
                _audit("subtle-spell", "Metamagic: Subtle Spell", "class", combat_relevant=False, automated=True,
                       notes="Component removal is arena-neutral in the current Pit."),
            ]
        if level >= 3:
            audits += [
                _audit("draconic-sorcery", "Draconic Sorcery", "subclass", combat_relevant=True, automated=True,
                       notes="2024 subclass begins at level 3 and always prepares its Draconic spells."),
                _audit("draconic-resilience", "Draconic Resilience", "subclass", combat_relevant=True, automated=True,
                       notes="HP maximum +3 then +1 per later Sorcerer level. Unarmored AC is 10 + Dex + Cha."),
                _audit("dragons-breath", "Dragon's Breath", "subclass", combat_relevant=True, automated=True,
                       notes="Action starts Concentration; later Magic actions exhale a 15-foot Fire cone, Dexterity save, 3d6, half on success."),
            ]
        if level >= 4:
            audits.append(_audit(
                "ability-score-improvement-l4", "Ability Score Improvement", "class",
                combat_relevant=True, automated=True,
                notes="Raises Charisma 17→19 through the certified build profile.",
            ))
        if level >= 5:
            audits += [
                _audit("sorcerous-restoration", "Sorcerous Restoration", "class",
                       combat_relevant=False, automated=True,
                       notes="Short-Rest Sorcery Point recovery is between-fight; arena fights do not take a Short Rest."),
                _audit("fireball", "Fireball", "class", combat_relevant=True, automated=True,
                       notes="Uses the universal 2024 Fireball fingerprint."),
            ]
        audits.extend(build_nyra_2024_high_audits(level))
        return audits
    except Exception:
        logger.exception("Failed to build Nyra's 2024 Draconic audits at level %s.", level)
        raise

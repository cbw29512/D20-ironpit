from __future__ import annotations

import logging

from app.content.wizard_evoker_2024_high_audits import build_elian_2024_high_audits
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


def build_elian_evoker_2024_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit("human", "Human", "species", combat_relevant=True, automated=True,
                   notes="2024 Human supplies Resourceful, Skillful, and Versatile."),
            _audit("resourceful", "Resourceful", "species", combat_relevant=True, automated=True,
                   notes="Fresh-rest arena initialization starts Elian with Heroic Inspiration."),
            _audit("skillful", "Skillful", "species", combat_relevant=False, automated=True,
                   notes="Canonical extra skill is Religion."),
            _audit("versatile", "Versatile", "species", combat_relevant=False, automated=True,
                   notes="Recommended Skilled Origin feat selected."),
            _audit("skilled", "Skilled", "feat", combat_relevant=False, automated=True,
                   notes="Medicine, Nature, and Perception proficiencies selected."),
            _audit(
                "magic-initiate-wizard", "Magic Initiate (Wizard)", "feat",
                combat_relevant=False, automated=False,
                notes="Sage origin feat. Canonical Wizard choices stay arena-neutral.",
            ),
            _audit(
                "dagger", "Dagger", "equipment", combat_relevant=True, automated=True,
                runtime_attack_weapon_id="dagger",
                notes="2024 starting dagger is the mundane fallback; Wizard has no Weapon Mastery.",
            ),
            _audit("spellcasting", "Spellcasting", "class", combat_relevant=True, automated=True,
                   notes="Prepared Wizard spells use Intelligence and the full-caster slot table."),
            _audit("ritual-adept", "Ritual Adept", "class", combat_relevant=False, automated=True,
                   notes="Ritual casting is between-fight and does not change a single Pit encounter."),
            _audit("arcane-recovery", "Arcane Recovery", "class", combat_relevant=False, automated=True,
                   notes="Short-Rest slot recovery is between-fight."),
            _audit("fire-bolt", "Fire Bolt", "class", combat_relevant=True, automated=True,
                   notes="Uses the universal 2024 Fire Bolt fingerprint."),
            _audit("poison-spray", "Poison Spray", "class", combat_relevant=True, automated=True,
                   notes="Uses the universal 2024 Poison Spray attack fingerprint."),
            _audit("thunderclap", "Thunderclap", "class", combat_relevant=True, automated=True,
                   notes="Uses the universal 2024 Thunderclap fingerprint."),
            _audit("burning-hands", "Burning Hands", "class", combat_relevant=True, automated=True,
                   notes="Uses the universal 2024 Burning Hands fingerprint."),
            _audit("magic-missile", "Magic Missile", "class", combat_relevant=True, automated=True,
                   notes="Three 1d4+1 Force darts; one extra dart per slot above 1."),
        ]
        if level >= 2:
            audits.append(_audit(
                "scholar", "Scholar", "class", combat_relevant=False, automated=True,
                notes="Expertise in Arcana. Skill checks are not a Pit combat resolver.",
            ))
        if level >= 3:
            audits += [
                _audit("evoker", "Evoker", "subclass", combat_relevant=True, automated=True,
                       notes="2024 subclass begins at level 3."),
                _audit("evocation-savant", "Evocation Savant", "subclass",
                       combat_relevant=False, automated=True,
                       notes="Spellbook copying time and gold are outside arena combat."),
                _audit(
                    "potent-cantrip", "Potent Cantrip", "subclass",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Missed attack cantrips and successful-save cantrips deal half damage "
                        "and no extra effect."
                    ),
                ),
            ]
        if level >= 4:
            audits.append(_audit(
                "ability-score-improvement-l4", "Ability Score Improvement", "class",
                combat_relevant=True, automated=True,
                notes="Raises Intelligence 17→19 through the certified build profile.",
            ))
        if level >= 5:
            audits += [
                _audit("memorize-spell", "Memorize Spell", "class",
                       combat_relevant=False, automated=True,
                       notes="Between-fight replacement of one prepared spell after a Short Rest."),
                _audit("fireball", "Fireball", "class", combat_relevant=True, automated=True,
                       notes="Uses the universal 2024 Fireball fingerprint."),
            ]
        audits.extend(build_elian_2024_high_audits(level))
        return audits
    except Exception:
        logger.exception("Failed to build Elian's 2024 Evoker audits at level %s.", level)
        raise

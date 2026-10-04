from __future__ import annotations

import logging

from app.content.canonical_spell_packages import build_class_spell_package
from app.content.bard_2014_spell_package import build_bard_2014_spell_package
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.druid_2014_spell_package import build_druid_2014_spell_package
from app.content.paladin_2014_spell_package import build_paladin_2014_spell_package
from app.content.ranger_2014_spell_package import build_ranger_2014_spell_package
from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.warlock_2014_spell_package import build_warlock_2014_spell_package
from app.content.sorcerer_2024_spell_package import build_sorcerer_2024_spell_package
from app.content.warlock_2024_spell_package import build_warlock_2024_spell_package
from app.content.wizard_2014_spell_package import build_wizard_2014_spell_package
from app.domain.character_builds import RulesetId
from app.domain.class_loadouts import ClassSpellPackage

logger = logging.getLogger(__name__)

CASTER_CLASS_IDS = frozenset({
    "bard", "cleric", "druid", "paladin", "ranger", "sorcerer", "warlock", "wizard",
})


def _require_casting_modifier(class_id: str, ability: str, casting_modifier: int | None) -> int:
    if casting_modifier is None:
        raise ValueError(f"2014 {class_id.title()} spell preparation requires the {ability} modifier.")
    return casting_modifier


def _canonical_spell_package_2014(
    class_id: str,
    level: int,
    casting_modifier: int | None,
) -> ClassSpellPackage | None:
    if class_id == "bard":
        return build_bard_2014_spell_package(level)
    if class_id == "cleric":
        return build_cleric_2014_spell_package(level, _require_casting_modifier(class_id, "Wisdom", casting_modifier))
    if class_id == "druid":
        return build_druid_2014_spell_package(level, _require_casting_modifier(class_id, "Wisdom", casting_modifier))
    if class_id == "paladin":
        return build_paladin_2014_spell_package(level, _require_casting_modifier(class_id, "Charisma", casting_modifier))
    if class_id == "ranger":
        return None if level < 2 else build_ranger_2014_spell_package(level)
    if class_id == "sorcerer":
        return build_sorcerer_2014_spell_package(level)
    if class_id == "warlock":
        return build_warlock_2014_spell_package(level)
    if class_id == "wizard":
        return build_wizard_2014_spell_package(
            level,
            _require_casting_modifier(class_id, "Intelligence", casting_modifier),
        )
    return None


def canonical_spell_package(
    class_id: str,
    level: int,
    ruleset: RulesetId = "2024",
    casting_modifier: int | None = None,
) -> ClassSpellPackage | None:
    """Return the edition-correct canonical spell package for one hero snapshot."""
    try:
        if class_id not in CASTER_CLASS_IDS:
            return None
        if ruleset == "2014":
            return _canonical_spell_package_2014(class_id, level, casting_modifier)
        if class_id == "warlock":
            return build_warlock_2024_spell_package(level)
        if class_id == "sorcerer":
            return build_sorcerer_2024_spell_package(level)
        return build_class_spell_package(class_id, level)  # type: ignore[arg-type]
    except Exception:
        logger.exception("Failed to resolve %s %s spell package at level %s.", ruleset, class_id, level)
        raise

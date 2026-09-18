from __future__ import annotations

from app.content.canonical_spell_packages import build_class_spell_package
from app.content.paladin_2014_spell_package import build_paladin_2014_spell_package
from app.domain.character_builds import RulesetId
from app.domain.class_loadouts import ClassSpellPackage

CASTER_CLASS_IDS = frozenset({
    "bard", "cleric", "druid", "paladin", "ranger", "sorcerer", "warlock", "wizard",
})


def canonical_spell_package(
    class_id: str,
    level: int,
    ruleset: RulesetId = "2024",
    casting_modifier: int | None = None,
) -> ClassSpellPackage | None:
    """Return the edition-correct canonical spell package for one hero snapshot."""
    if class_id not in CASTER_CLASS_IDS:
        return None
    if ruleset == "2014":
        if class_id != "paladin":
            return None
        if casting_modifier is None:
            raise ValueError("2014 Paladin spell preparation requires the Charisma modifier.")
        return build_paladin_2014_spell_package(level, casting_modifier)
    return build_class_spell_package(class_id, level)  # type: ignore[arg-type]

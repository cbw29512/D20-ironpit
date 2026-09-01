from __future__ import annotations

from collections.abc import Iterable

from app.content.canonical_spell_packages import build_class_spell_package
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.melee_loadout_policy import choose_melee_loadout
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit
from app.domain.class_loadouts import ClassSpellPackage, MeleeLoadoutSelection

CASTER_CLASS_IDS = frozenset({
    "bard", "cleric", "druid", "paladin", "ranger", "sorcerer", "warlock", "wizard",
})


def canonical_template_id(class_id: str, level: int) -> str:
    if class_id not in HERO_BY_CLASS:
        raise ValueError(f"Unknown canonical class: {class_id}.")
    if not 1 <= level <= 20:
        raise ValueError("Canonical hero level must be between 1 and 20.")
    slug = HERO_BY_CLASS[class_id].hero_name.lower().replace(" ", "-")
    return f"{slug}-l{level}"


def canonical_subclass_id(class_id: str, level: int) -> str | None:
    if class_id not in HERO_BY_CLASS:
        raise ValueError(f"Unknown canonical class: {class_id}.")
    if not 1 <= level <= 20:
        raise ValueError("Canonical hero level must be between 1 and 20.")
    return HERO_BY_CLASS[class_id].subclass_id if level >= 3 else None


def assert_canonical_identity(class_id: str, hero_name: str, level: int) -> None:
    hero = HERO_BY_CLASS.get(class_id)
    if hero is None:
        raise ValueError(f"Unknown canonical class: {class_id}.")
    if hero_name != hero.hero_name:
        raise ValueError(f"{class_id} must progress as {hero.hero_name}, not {hero_name}.")
    canonical_template_id(class_id, level)


def combat_feature_audits(audits: Iterable[FeatureAudit]) -> list[FeatureAudit]:
    """Return only features capable of changing an Iron Pit combat outcome."""
    return [audit for audit in audits if audit.combat_relevant]


def canonical_spell_package(class_id: str, level: int) -> ClassSpellPackage | None:
    if class_id not in CASTER_CLASS_IDS:
        return None
    return build_class_spell_package(class_id, level)  # type: ignore[arg-type]


def canonical_melee_loadout(
    profile: CharacterBuildProfile,
    *,
    shield_trained: bool,
    power_build: bool = False,
    dual_wield_trained: bool = True,
) -> MeleeLoadoutSelection:
    scores = profile.final_ability_scores
    return choose_melee_loadout(
        scores.strength,
        scores.dexterity,
        shield_trained=shield_trained,
        power_build=power_build,
        dual_wield_trained=dual_wield_trained,
    )

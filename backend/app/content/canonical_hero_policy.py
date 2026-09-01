from __future__ import annotations

from collections.abc import Iterable

from app.content.canonical_spell_packages import build_class_spell_package
from app.content.hero_progressions import COMBAT_PLAN_BY_CLASS, HERO_BY_CLASS
from app.content.melee_loadout_policy import choose_melee_loadout
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit
from app.domain.class_loadouts import (
    CanonicalCombatPlan,
    ClassSpellPackage,
    MeleeLoadoutSelection,
)

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


def canonical_combat_plan(class_id: str) -> CanonicalCombatPlan:
    plan = COMBAT_PLAN_BY_CLASS.get(class_id)
    if plan is None:
        raise ValueError(f"Unknown canonical class: {class_id}.")
    return plan


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


def canonical_melee_loadout(profile: CharacterBuildProfile) -> MeleeLoadoutSelection | None:
    plan = canonical_combat_plan(profile.class_id)
    if plan.mode == "caster":
        return None
    if plan.forced_melee_kind == "unarmed":
        return MeleeLoadoutSelection(kind="unarmed", primary_ability="dexterity")
    scores = profile.final_ability_scores
    return choose_melee_loadout(
        scores.strength,
        scores.dexterity,
        shield_trained=plan.shield_trained,
        power_build=plan.power_build,
        dual_wield_trained=plan.dual_wield_trained,
    )


def assert_canonical_profile_policy(profile: CharacterBuildProfile) -> None:
    hero = HERO_BY_CLASS.get(profile.class_id)
    if hero is None:
        raise ValueError(f"Unknown canonical class: {profile.class_id}.")
    assert_canonical_identity(profile.class_id, profile.character_name, profile.level)
    if profile.class_name != hero.class_name:
        raise ValueError(
            f"{profile.class_id} canonical class name drifted: {profile.class_name} != {hero.class_name}."
        )
    expected_template_id = canonical_template_id(profile.class_id, profile.level)
    if profile.template_id != expected_template_id:
        raise ValueError(
            f"{profile.class_id} level {profile.level} canonical template drifted: "
            f"{profile.template_id} != {expected_template_id}."
        )

    plan = canonical_combat_plan(profile.class_id)
    if plan.mode in {"caster", "hybrid"}:
        canonical_spell_package(profile.class_id, profile.level)
    expected_loadout = canonical_melee_loadout(profile)
    expected_kind = expected_loadout.kind if expected_loadout else None
    if profile.combat_loadout_kind != expected_kind:
        raise ValueError(
            f"{profile.class_id} level {profile.level} canonical loadout drifted: "
            f"{profile.combat_loadout_kind} != {expected_kind}."
        )

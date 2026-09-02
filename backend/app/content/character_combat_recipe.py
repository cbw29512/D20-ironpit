from __future__ import annotations

from dataclasses import dataclass

from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.combat_build_choice_overlays import CombatBuildChoiceOverlay, maybe_combat_build_choice_overlay
from app.content.combat_build_variants import CombatBuildStatus, get_combat_build_variant


@dataclass(frozen=True)
class CharacterCombatRecipe:
    class_id: str
    subclass_id: str
    build_id: str
    level: int
    role: str
    build_status: CombatBuildStatus
    shared_progression_id: str
    combat_features: tuple[str, ...]
    build_choices: CombatBuildChoiceOverlay | None = None


def compose_character_combat_recipe(
    class_id: str,
    subclass_id: str,
    build_id: str,
    level: int,
) -> CharacterCombatRecipe:
    """Compose class spine + sparse subclass + combat-build choices without duplicating level data."""
    variant = get_combat_build_variant(class_id, build_id)
    required = variant.required_subclass_id
    if required is not None and subclass_id != required:
        raise ValueError(
            f"{class_id} build {build_id} requires subclass {required}, not {subclass_id}."
        )
    features = canonical_combat_features(class_id, level, subclass_id)
    return CharacterCombatRecipe(
        class_id=class_id,
        subclass_id=subclass_id,
        build_id=build_id,
        level=level,
        role=variant.role,
        build_status=variant.status,
        shared_progression_id=variant.shared_progression_id,
        combat_features=features,
        build_choices=maybe_combat_build_choice_overlay(class_id, build_id),
    )

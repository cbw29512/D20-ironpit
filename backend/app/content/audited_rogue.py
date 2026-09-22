from __future__ import annotations

from app.content.canonical_hero_policy import canonical_template_id
from app.content.canonical_progression import advance_template_data
from app.content.character_math import fixed_hit_points
from app.content.class_subclass_composer import base_class_combat_features, compose_class_subclass_features
from app.content.hero_combat_feature_registry import compile_progression_feature_fields, unsupported_hero_engine_features
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.progression_saves import saving_throw_proficiencies
from app.content.rogue_attacks import build_mara_shortbow_attack, build_mara_shortsword_attack
from app.content.rogue_combat_levels import ROGUE_COMBAT_LEVELS
from app.content.rogue_equipment import build_rogue_visual_loadout
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, ResourceDefinition
from app.domain.progression import ProgressionCombatFeatures
from app.domain.traits import CombatTrait


def mara_rogue_features(level: int) -> tuple[str, ...]:
    if level < 3:
        return base_class_combat_features("rogue", level, ROGUE_COMBAT_LEVELS)
    return compose_class_subclass_features("rogue", "thief", level, ROGUE_COMBAT_LEVELS)


_MARA_ARENA_INERT_FEATURES = frozenset({
    "thief-fast-hands", "thief-supreme-sneak", "thief-use-magic-device",
    "rogue-epic-boon",
})


def unsupported_mara_rogue_features(level: int) -> tuple[str, ...]:
    active = tuple(
        feature for feature in mara_rogue_features(level)
        if feature not in _MARA_ARENA_INERT_FEATURES
    )
    return unsupported_hero_engine_features(active)


def _level_one_scores() -> AbilityScores:
    return AbilityScores(
        strength=13, dexterity=17, constitution=15,
        intelligence=10, wisdom=10, charisma=10,
    )


def _scores_after_level_delta(previous: AbilityScores, level: int) -> AbilityScores:
    if level == 4:
        return previous.model_copy(update={"dexterity": 18, "constitution": 16})
    if level == 8:
        return previous.model_copy(update={"dexterity": 20})
    if level == 10:
        return previous.model_copy(update={"constitution": 18})
    if level == 12:
        return previous.model_copy(update={"constitution": 20})
    if level == 16:
        return previous.model_copy(update={"wisdom": 12})
    if level == 19:
        return previous.model_copy(update={"strength": 14})
    return previous.model_copy()


def _apply_level_delta(data: dict[str, object], level: int, scores: AbilityScores) -> None:
    row = ROGUE_COMBAT_LEVELS[level]
    dexterity_mod = scores.modifier("dexterity")
    constitution_mod = scores.modifier("constitution")
    strength_mod = scores.modifier("strength")
    intelligence_mod = scores.modifier("intelligence")
    attack_bonus = row.proficiency_bonus + dexterity_mod
    progression_fields = compile_progression_feature_fields(mara_rogue_features(level), level)
    progression = ProgressionCombatFeatures.model_validate(progression_fields)
    save_proficiencies = saving_throw_proficiencies(("dexterity", "intelligence"), progression)

    def save_bonus(ability: str, modifier: int) -> int:
        return modifier + (row.proficiency_bonus if ability in save_proficiencies else 0)

    data.update(
        ability_scores=scores.model_dump(),
        armor_class=11 + dexterity_mod,
        max_hp=fixed_hit_points(level, 8, constitution_mod),
        initiative_bonus=dexterity_mod,
        weapon_attack=build_mara_shortsword_attack(
            attack_bonus=attack_bonus, damage_bonus=dexterity_mod,
        ).model_dump(),
        alternate_weapon_attacks=[build_mara_shortbow_attack(
            attack_bonus=attack_bonus, damage_bonus=dexterity_mod,
        ).model_dump()],
        saving_throw_bonuses={
            "strength": save_bonus("strength", strength_mod),
            "dexterity": save_bonus("dexterity", dexterity_mod),
            "constitution": save_bonus("constitution", constitution_mod),
            "intelligence": save_bonus("intelligence", intelligence_mod),
            "wisdom": save_bonus("wisdom", scores.modifier("wisdom")),
            "charisma": save_bonus("charisma", scores.modifier("charisma")),
        },
        skill_bonuses={
            "athletics": row.proficiency_bonus + strength_mod,
            "acrobatics": row.proficiency_bonus + dexterity_mod,
        },
        progression_features=progression_fields,
        resources=[
            ResourceDefinition(id="adrenaline-rush", name="Adrenaline Rush", max_uses=row.proficiency_bonus).model_dump(),
            ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1).model_dump(),
            *(
                [ResourceDefinition(id="stroke-of-luck", name="Stroke of Luck", max_uses=1).model_dump()]
                if level >= 20 else []
            ),
        ],
        source=f"D&D Beyond Basic Rules 2024: Rogue {level}, Orc, Soldier, Savage Attacker, Leather Armor, Shortsword, Shortbow, Vex",
    )


def _build_level_one() -> CombatantTemplate:
    hero = HERO_BY_CLASS["rogue"]
    scores = _level_one_scores()
    data = {
        "id": canonical_template_id("rogue", 1),
        "name": hero.hero_name, "archetype": hero.class_name, "level": 1, "kind": "character",
        "speed_ft": 30,
        "combat_traits": [
            CombatTrait.SAVAGE_ATTACKER, CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE,
        ],
        "weapon_masteries": ["shortsword", "shortbow"],
        "visual": build_rogue_visual_loadout().model_dump(),
    }
    _apply_level_delta(data, 1, scores)
    return CombatantTemplate.model_validate(data)


def build_mara_quickstep_level(level: int) -> CombatantTemplate:
    """Advance one persistent Mara Quickstep progression from the canonical level-1 foundation."""
    if level not in ROGUE_COMBAT_LEVELS:
        raise ValueError(f"Mara Rogue level {level} must be between 1 and 20.")
    unsupported = unsupported_mara_rogue_features(level)
    if unsupported:
        raise ValueError(f"Mara Rogue level {level} awaits combat support for: {', '.join(unsupported)}")
    if level == 1:
        return _build_level_one()

    previous = build_mara_quickstep_level(level - 1)
    if previous.ability_scores is None:
        raise ValueError(f"Mara Rogue level {level - 1} is missing canonical ability scores.")
    data = advance_template_data(previous, "rogue", level)
    _apply_level_delta(data, level, _scores_after_level_delta(previous.ability_scores, level))
    return CombatantTemplate.model_validate(data)

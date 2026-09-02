from __future__ import annotations

from app.content.fighter_champion_profile_features import (
    advancement_audit,
    fighting_style_audit,
    shared_fighter_champion_feature_audits,
)
from app.content.fighter_champion_variant_specs import FIGHTER_CHAMPION_VARIANT_SPECS, FighterChampionVariantSpec
from app.content.hero_progressions import HERO_BY_CLASS
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile

_BACKGROUND_EQUIPMENT = (
    "Spear", "Shortbow", "20 Arrows", "Gaming Set", "Healer's Kit",
    "Quiver", "Traveler's Clothes", "14 GP",
)


def _apply(scores: AbilityScores, increases: tuple[AbilityIncrease, ...], cap: int) -> AbilityScores:
    data = scores.model_dump()
    for increase in increases:
        value = data[increase.ability] + increase.amount
        if value > cap:
            raise ValueError(f"{increase.ability.title()} increase exceeds its {cap} cap.")
        data[increase.ability] = value
    return AbilityScores(**data)


def _scores(spec: FighterChampionVariantSpec, level: int) -> tuple[AbilityScores, list[AbilityIncrease]]:
    scores = _apply(spec.base_scores, spec.background_increases, 20)
    advancement: list[AbilityIncrease] = []
    for current in (4, 6, 8, 12, 14, 16):
        if current <= level:
            increases = spec.asi_plan[current]
            scores = _apply(scores, increases, 20)
            advancement.extend(increases)
    if level >= 19:
        boon = AbilityIncrease(ability=spec.boon_ability, amount=1)
        scores = _apply(scores, (boon,), 30)
        advancement.append(boon)
    return scores, advancement


def _masteries(spec: FighterChampionVariantSpec, level: int) -> list[str]:
    count = 3 if level < 4 else 4 if level < 10 else 5 if level < 16 else 6
    return list(spec.mastery_priority[:count])


def _style_audits(spec: FighterChampionVariantSpec, level: int):
    audits = [fighting_style_audit(spec.fighting_styles[0])]
    if level >= 7:
        audits.append(fighting_style_audit(spec.fighting_styles[1], additional=True))
    return audits


def _advancement_audits(spec: FighterChampionVariantSpec, level: int):
    audits = []
    for current in (4, 6, 8, 12, 14, 16):
        if current <= level:
            text = ", ".join(f"+{item.amount} {item.ability.title()}" for item in spec.asi_plan[current])
            audits.append(advancement_audit(current, text))
    if level >= 19:
        audits.append(advancement_audit(
            19,
            f"Boon of Combat Prowess: +1 {spec.boon_ability.title()}; Peerless Aim remains runtime-blocked.",
        ))
    return audits


def _skills(spec: FighterChampionVariantSpec) -> list[str]:
    if spec.primary_ability == "dexterity":
        return ["Athletics", "Intimidation", "Acrobatics", "Perception"]
    return ["Athletics", "Intimidation", "Perception", "Survival"]


def build_fighter_champion_variant_profile(build_id: str, level: int) -> CharacterBuildProfile:
    if not 3 <= level <= 20:
        raise ValueError("Champion variants branch from the shared Fighter at levels 3-20.")
    try:
        spec = FIGHTER_CHAMPION_VARIANT_SPECS[build_id]
    except KeyError as exc:
        raise ValueError(f"Unknown Fighter Champion variant: {build_id}.") from exc
    hero = HERO_BY_CLASS["fighter"]
    scores, advancement = _scores(spec, level)
    styles = list(spec.fighting_styles[:1 if level < 7 else 2])
    audits = [
        *shared_fighter_champion_feature_audits(level),
        *_style_audits(spec, level),
        *_advancement_audits(spec, level),
    ]
    return CharacterBuildProfile(
        id=f"build-{hero.hero_name.lower().replace(' ', '-')}-{build_id}-l{level}",
        template_id=f"fighter-champion-{build_id}-l{level}",
        character_name=hero.hero_name,
        class_id="fighter", class_name=hero.class_name, level=level,
        subclass_id="champion", subclass_name="Champion", build_id=build_id,
        species_id="orc", species_name="Orc", background_id="soldier", background_name="Soldier",
        origin_feat_id="savage-attacker", origin_feat_name="Savage Attacker",
        base_ability_scores=spec.base_scores,
        background_allowed_abilities=["strength", "dexterity", "constitution"],
        background_increases=list(spec.background_increases), advancement_increases=advancement,
        final_ability_scores=scores,
        class_equipment_option=spec.class_equipment_option, class_equipment=list(spec.class_equipment),
        background_equipment_option="package", background_equipment=list(_BACKGROUND_EQUIPMENT),
        skill_proficiencies=_skills(spec), weapon_masteries=_masteries(spec, level),
        fighting_style=styles[0], fighting_styles=styles, combat_loadout_kind=spec.loadout_kind,
        feature_audits=audits,
        source_references=[
            "D&D Beyond Basic Rules 2024: Fighter",
            "D&D Beyond Basic Rules 2024: Champion",
            "D&D Beyond Basic Rules 2024: Fighter Starting Equipment and Fighting Style Feats",
            "D&D Beyond Basic Rules 2024: Ability Score Improvement and Boon of Combat Prowess",
        ],
    )


def fighter_champion_variant_profiles() -> tuple[CharacterBuildProfile, ...]:
    return tuple(
        build_fighter_champion_variant_profile(build_id, level)
        for build_id in FIGHTER_CHAMPION_VARIANT_SPECS
        for level in range(3, 21)
    )

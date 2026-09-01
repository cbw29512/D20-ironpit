from __future__ import annotations

from app.content.audited_barbarian import build_rokhan_stonefury
from app.content.canonical_progression import advance_template_data
from app.content.level_resources import barbarian_rage_uses, fixed_class_hit_points, orc_adrenaline_rush_uses
from app.domain.models import CombatantTemplate, ResourceDefinition


def _resources(level: int) -> list[ResourceDefinition]:
    return [
        ResourceDefinition(id="rage", name="Rage", max_uses=barbarian_rage_uses(level)),
        ResourceDefinition(id="adrenaline-rush", name="Adrenaline Rush", max_uses=orc_adrenaline_rush_uses(level)),
        ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
    ]


def _apply_level_four_advancement(data: dict[str, object]) -> None:
    primary = data["weapon_attack"]
    alternates = data["alternate_weapon_attacks"]
    saves = data["saving_throw_bonuses"]
    skills = data["skill_bonuses"]
    masteries = data["weapon_masteries"]
    if not isinstance(primary, dict) or not isinstance(alternates, list) or not isinstance(saves, dict) or not isinstance(skills, dict) or not isinstance(masteries, list):
        raise ValueError("Rokhan Barbarian 4 base snapshot has an unexpected schema.")
    strength_attacks = [primary, *(item for item in alternates if isinstance(item, dict) and item.get("attack_ability") == "strength")]
    for attack in strength_attacks:
        attack["attack_bonus"] = 6
        attack["damage_bonus"] = 4
    saves.update(strength=6, constitution=5)
    skills["athletics"] = 6
    masteries.append("longsword")
    data["armor_class"] = 14


def build_rokhan_stonefury_level(level: int) -> CombatantTemplate:
    """Advance the canonical Barbarian one certified level at a time; unsupported levels fail closed."""
    if level == 1:
        return build_rokhan_stonefury()
    if level not in (2, 3, 4):
        raise ValueError(f"Rokhan Barbarian level {level} is not certified yet.")

    previous = build_rokhan_stonefury_level(level - 1)
    data = advance_template_data(previous, "barbarian", level)
    features = dict(data["progression_features"])
    source_level = {
        2: "Barbarian Level 2",
        3: "Barbarian Level 3, Path of the Berserker",
        4: "Barbarian Level 4 Ability Score Improvement",
    }[level]
    if level == 2:
        features.update(danger_sense=True, reckless_attack=True)
    if level == 3:
        features.update(frenzy=True)
    constitution_modifier = 3 if level >= 4 else 2
    data.update(
        max_hp=fixed_class_hit_points(level, 12, constitution_modifier),
        progression_features=features,
        resources=[item.model_dump() for item in _resources(level)],
        source=f"D&D Beyond Basic Rules 2024: {source_level}, Orc, Soldier, Savage Attacker, Equipment",
    )
    if level == 4:
        _apply_level_four_advancement(data)
    return CombatantTemplate.model_validate(data)

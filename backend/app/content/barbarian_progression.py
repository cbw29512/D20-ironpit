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


def build_rokhan_stonefury_level(level: int) -> CombatantTemplate:
    """Advance the canonical Barbarian one certified level at a time; unsupported levels fail closed."""
    if level == 1:
        return build_rokhan_stonefury()
    if level not in (2, 3):
        raise ValueError(f"Rokhan Barbarian level {level} is not certified yet.")

    previous = build_rokhan_stonefury() if level == 2 else build_rokhan_stonefury_level(2)
    data = advance_template_data(previous, "barbarian", level)
    features = dict(data["progression_features"])
    if level == 2:
        features.update(danger_sense=True, reckless_attack=True)
        source_level = "Barbarian Level 2"
    else:
        features.update(frenzy=True)
        source_level = "Barbarian Level 3, Path of the Berserker"
    data.update(
        max_hp=fixed_class_hit_points(level, 12, 2),
        progression_features=features,
        resources=[item.model_dump() for item in _resources(level)],
        source=f"D&D Beyond Basic Rules 2024: {source_level}, Orc, Soldier, Savage Attacker, Equipment",
    )
    return CombatantTemplate.model_validate(data)

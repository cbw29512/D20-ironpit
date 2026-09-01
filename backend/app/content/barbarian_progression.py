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
    if level != 2:
        raise ValueError(f"Rokhan Barbarian level {level} is not certified yet.")

    previous = build_rokhan_stonefury()
    data = advance_template_data(previous, "barbarian", 2)
    data.update(
        max_hp=fixed_class_hit_points(2, 12, 2),
        progression_features={
            **data["progression_features"],
            "danger_sense": True,
            "reckless_attack": True,
        },
        resources=[item.model_dump() for item in _resources(2)],
        source="D&D Beyond Basic Rules 2024: Barbarian Level 2, Orc, Soldier, Savage Attacker, Equipment",
    )
    return CombatantTemplate.model_validate(data)

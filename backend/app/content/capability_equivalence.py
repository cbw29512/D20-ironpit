from __future__ import annotations

from app.domain.models import CombatantTemplate


def semantic_template_dump(template: CombatantTemplate) -> dict[str, object]:
    """Normalize representation-only fields that cannot affect combat outcomes."""
    data = template.model_dump(mode="json")
    data.pop("creature_type", None)
    attacks = [data["weapon_attack"], *data["alternate_weapon_attacks"]]
    for attack in attacks:
        if attack["fixed_damage"] is not None:
            attack["weapon"]["dice_count"] = 0
            attack["weapon"]["dice_size"] = 2
    return data


def templates_semantically_equal(left: CombatantTemplate, right: CombatantTemplate) -> bool:
    return semantic_template_dump(left) == semantic_template_dump(right)

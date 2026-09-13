from __future__ import annotations

from app.content.basic_condition_actions import WAKE_SLEEPER_ID
from app.domain.models import CombatantTemplate


def _without_engine_global_actions(data: dict[str, object]) -> None:
    """Remove engine-provided defaults that are not immutable monster content."""
    actions = data.get("condition_removal_actions")
    if isinstance(actions, list):
        data["condition_removal_actions"] = [
            action for action in actions
            if not isinstance(action, dict) or action.get("id") != WAKE_SLEEPER_ID
        ]


def semantic_template_dump(template: CombatantTemplate) -> dict[str, object]:
    """Normalize representation-only fields that cannot affect combat outcomes."""
    data = template.model_dump(mode="json")
    data.pop("creature_type", None)
    _without_engine_global_actions(data)
    attacks = [data["weapon_attack"], *data["alternate_weapon_attacks"]]
    for attack in attacks:
        if attack["fixed_damage"] is not None:
            attack["weapon"]["dice_count"] = 0
            attack["weapon"]["dice_size"] = 2
    return data


def templates_semantically_equal(left: CombatantTemplate, right: CombatantTemplate) -> bool:
    return semantic_template_dump(left) == semantic_template_dump(right)

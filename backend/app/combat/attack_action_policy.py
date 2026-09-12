from __future__ import annotations

from app.combat.dice import DiceProvider
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import BattleEvent


def expanded_slots(definition: AttackActionDefinition, dice: DiceProvider) -> list[tuple[int, AttackActionSlot]]:
    policy = definition.policy
    if policy is None or policy.repeat_slot_index is None:
        return list(enumerate(definition.slots))
    repeats = sum(dice.roll(policy.repeat_dice_size) for _ in range(policy.repeat_dice_count))
    result: list[tuple[int, AttackActionSlot]] = []
    for index, slot in enumerate(definition.slots):
        count = repeats if index == policy.repeat_slot_index else 1
        result.extend((index, slot) for _ in range(count))
    return result


def slot_allowed(definition: AttackActionDefinition, slot_index: int, previous_event: BattleEvent | None) -> bool:
    policy = definition.policy
    if policy is None or slot_index not in policy.requires_previous_hit_slots:
        return True
    return previous_event is not None and previous_event.hit is True


def required_target_id(
    definition: AttackActionDefinition,
    slot_index: int,
    previous_event: BattleEvent | None,
) -> str | None:
    policy = definition.policy
    if policy is None or slot_index not in policy.same_target_as_previous_slots or previous_event is None:
        return None
    return previous_event.target_id


def filtered_slot(
    definition: AttackActionDefinition,
    slot: AttackActionSlot,
    used_attack_ids: set[str],
) -> AttackActionSlot:
    policy = definition.policy
    if policy is None or not policy.distinct_attack_ids:
        return slot
    return slot.model_copy(update={
        "attack_ids": [attack_id for attack_id in slot.attack_ids if attack_id not in used_attack_ids],
    })

from __future__ import annotations

from app.domain.capability_attacks import CapabilityActionSlot, MultiattackCapabilityDefinition
from app.domain.combat_sequence_ir import ActionChoiceSlotIR, ActionReferenceIR, ActionSequenceIR


def multiattack_capability_to_ir(action: MultiattackCapabilityDefinition) -> ActionSequenceIR:
    slots = []
    for slot in action.slots:
        options = [ActionReferenceIR(family="attack", action_id=action_id) for action_id in slot.attack_ids]
        options.extend(ActionReferenceIR(family="save", action_id=action_id) for action_id in slot.save_action_ids)
        slots.append(ActionChoiceSlotIR(options=options))
    return ActionSequenceIR(
        id=action.id,
        name=action.name,
        is_attack_action=action.is_attack_action,
        slots=slots,
    )


def multiattack_ir_to_capability(action: ActionSequenceIR) -> MultiattackCapabilityDefinition:
    slots = []
    for slot in action.slots:
        attack_ids = [option.action_id for option in slot.options if option.family == "attack"]
        save_action_ids = [option.action_id for option in slot.options if option.family == "save"]
        slots.append(CapabilityActionSlot(attack_ids=attack_ids, save_action_ids=save_action_ids))
    return MultiattackCapabilityDefinition(
        id=action.id,
        name=action.name,
        is_attack_action=action.is_attack_action,
        slots=slots,
    )

from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.attack_action_policy import AttackActionPolicy
from app.domain.weapons import WeaponAttack


def binding_executable_2014(source: CatalogMonster2014) -> bool:
    """Prove a source binding can be executed without inventing unresolved actions."""
    binding = source.multiattack_binding
    if binding is None:
        return bool(source.multiattack_slots)
    if binding.repeat_count_source is not None or any(slot.optional or slot.requirement for slot in binding.slots):
        return False
    attack_ids = {attack.id for attack in source.attacks}
    if any(any(action_id not in attack_ids for action_id in slot.action_ids) for slot in binding.slots):
        return False
    if binding.follow_up_action_id is None:
        return True
    action = next((item for item in source.swallow_actions if item.id == binding.follow_up_action_id), None)
    return bool(
        action is not None and action.attack_id is None and action.requires_existing_grapple
        and binding.follow_up_grapple_escape_dc is not None and binding.follow_up_max_target_size is not None
    )


def _policy(source: CatalogMonster2014) -> AttackActionPolicy | None:
    binding = source.multiattack_binding
    if binding is None or binding.follow_up_action_id is None:
        return source.multiattack_policy
    base = source.multiattack_policy or AttackActionPolicy()
    return base.model_copy(update={
        "follow_up_action_id": binding.follow_up_action_id,
        "follow_up_condition": binding.follow_up_condition,
        "follow_up_grapple_escape_dc": binding.follow_up_grapple_escape_dc,
        "follow_up_max_target_size": binding.follow_up_max_target_size,
    })


def compile_multiattack_2014(
    source: CatalogMonster2014,
    attacks: list[WeaponAttack],
) -> AttackActionDefinition | None:
    """Compile only source-faithful Multiattack slots whose actions are executable."""
    binding = source.multiattack_binding
    if binding is not None and not source.multiattack_slots:
        if not binding_executable_2014(source):
            raise ValueError(f"Bound Multiattack for {source.id} still references unresolved actions.")
        raw_slots = [slot.action_ids for slot in binding.slots]
    else:
        raw_slots = source.multiattack_slots
    if not raw_slots:
        return None
    attack_ids = {attack.id for attack in attacks}
    save_ids = {action.id for action in source.saving_throw_actions}
    slots: list[AttackActionSlot] = []
    for choices in raw_slots:
        if not choices:
            raise ValueError(f"Empty Multiattack slot for {source.id}.")
        attacks_here = [choice for choice in choices if choice in attack_ids]
        saves_here = [choice for choice in choices if choice in save_ids]
        if len(attacks_here) + len(saves_here) != len(choices):
            raise ValueError(f"Invalid Multiattack action ids for {source.id}: {choices}")
        if attacks_here and saves_here:
            raise ValueError(f"Mixed attack/save choices require separate slots for {source.id}: {choices}")
        slots.append(AttackActionSlot(attack_ids=attacks_here, save_action_ids=saves_here))
    return AttackActionDefinition(
        id=f"2014-{source.id}-multiattack", name="Multiattack", slots=slots, policy=_policy(source),
    )

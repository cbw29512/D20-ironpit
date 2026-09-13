from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.weapons import WeaponAttack


def compile_multiattack_2014(
    source: CatalogMonster2014,
    attacks: list[WeaponAttack],
) -> AttackActionDefinition | None:
    """Compile ordered printed Multiattack slots that may contain attacks or save actions."""
    if not source.multiattack_slots:
        return None
    attack_ids = {attack.id for attack in attacks}
    save_ids = {action.id for action in source.saving_throw_actions}
    slots: list[AttackActionSlot] = []
    for choices in source.multiattack_slots:
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
        id=f"2014-{source.id}-multiattack",
        name="Multiattack",
        slots=slots,
        policy=source.multiattack_policy,
    )

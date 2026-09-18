from __future__ import annotations

from app.combat.area_targeting import AreaPlacement, legal_area_placements
from app.combat.saving_throws import legal_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import SavingThrowAction


def legal_area_save_placements(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
) -> list[AreaPlacement]:
    if action.area is None:
        return []
    by_id = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
    filtered: dict[tuple[str, ...], AreaPlacement] = {}
    for placement in legal_area_placements(actor, setup, action.area, action.range_ft):
        targets = tuple(
            target_id for target_id in placement.target_ids
            if (target := by_id.get(target_id)) is not None and legal_save_action(action, target, 0)
        )
        if targets and targets not in filtered:
            filtered[targets] = AreaPlacement(
                target_ids=targets, origin=placement.origin,
                direction=placement.direction, friendly_ids=placement.friendly_ids,
            )
    return sorted(
        filtered.values(),
        key=lambda item: (-len(item.target_ids), len(item.friendly_ids), item.target_ids),
    )

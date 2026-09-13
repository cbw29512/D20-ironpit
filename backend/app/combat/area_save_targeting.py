from __future__ import annotations

from app.combat.area_targeting import AreaPlacement, legal_area_placements
from app.combat.save_control_effects import target_is_source_effect_immune
from app.combat.saving_throws import legal_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import SavingThrowAction


def legal_area_save_placements(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
) -> list[AreaPlacement]:
    """Return area placements after removing targets this action cannot affect."""
    if action.area is None:
        return []
    by_id = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
    filtered: dict[tuple[str, ...], AreaPlacement] = {}
    for placement in legal_area_placements(actor, setup, action.area, action.range_ft):
        target_ids = tuple(
            target_id
            for target_id in placement.target_ids
            if (
                (target := by_id.get(target_id)) is not None
                and legal_save_action(action, target, 0)
                and not target_is_source_effect_immune(actor, target, action)
            )
        )
        if not target_ids or target_ids in filtered:
            continue
        filtered[target_ids] = AreaPlacement(
            target_ids=target_ids,
            origin=placement.origin,
            direction=placement.direction,
        )
    return sorted(
        filtered.values(),
        key=lambda item: (-len(item.target_ids), item.target_ids, item.origin, item.direction or (0.0, 0.0)),
    )

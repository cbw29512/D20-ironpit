from __future__ import annotations

from app.combat.group_healing import choose_group_healing_targets, resolve_group_healing
from app.combat.healing import choose_healing_action, resolve_healing
from app.combat.replacement_form_triage import defer_self_healing_for_form
from app.combat.replacement_form_offense import defer_emergency_form_for_spell
from app.combat.healing_riders import apply_slot_healing_self_rider


def resolve_healing_support(
    sequence,
    round_number,
    healer,
    setup,
    dice,
    turn_key,
    *,
    downed_only: bool = False,
):
    choice = choose_healing_action(healer, setup, turn_key)
    if choice is None:
        return [], sequence
    action, target = choice
    # Never suppress ally rescue; only a competing self-heal can yield to form.
    if (not downed_only and target.combatant_id == healer.combatant_id
        and defer_self_healing_for_form(healer, action, turn_key)):
        form = next(item for item in healer.state.template.replacement_form_actions
                    if item.ai_use_policy == "emergency_only")
        if not defer_emergency_form_for_spell(healer, setup, form, turn_key):
            return [], sequence
    if action.max_targets > 1:
        targets = choose_group_healing_targets(healer, setup, action, turn_key)
        if downed_only and not any(item.state.current_hp == 0 for item in targets):
            return [], sequence
        if not targets:
            return [], sequence
        before = {item.combatant_id: item.state.current_hp for item in targets}
        events, sequence = resolve_group_healing(
            sequence, round_number, healer, targets, action, dice, turn_key,
            setup=setup,
        )
        healed_other = any(
            item.combatant_id != healer.combatant_id
            and item.state.current_hp > before[item.combatant_id]
            for item in targets
        )
    else:
        if downed_only and target.state.current_hp != 0:
            return [], sequence
        before = target.state.current_hp
        events = [resolve_healing(sequence, round_number, healer, target, action, dice, turn_key)]
        sequence += 1
        healed_other = (
            target.combatant_id != healer.combatant_id and target.state.current_hp > before
        )
    rider = apply_slot_healing_self_rider(
        sequence, round_number, healer, healed_other, action,
    )
    if rider is not None:
        events.append(rider)
        sequence += 1
    return events, sequence

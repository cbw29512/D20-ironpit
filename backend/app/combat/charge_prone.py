from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.charge_profiles import ChargeProfileDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.size import size_at_most

PRONE = "prone"


def _event_target(
    event: BattleEvent,
    fallback: EncounterCombatant,
    setup: EncounterSetup | None,
) -> EncounterCombatant:
    if setup is None:
        return fallback
    return next(
        (member for member in [*setup.heroes, *setup.monsters] if member.combatant_id == event.target_id),
        fallback,
    )


def resolve_charge_prone(
    event: BattleEvent,
    target: EncounterCombatant,
    profile: ChargeProfileDefinition,
    dice: DiceProvider,
    setup: EncounterSetup | None,
) -> BattleEvent:
    if not event.hit or profile.prone_save_dc is None or profile.prone_save_ability is None:
        return event
    actual = _event_target(event, target, setup)
    if actual.state.is_dead or not actual.state.is_alive or condition_is_immune(actual.state, PRONE):
        return event
    maximum = profile.prone_max_target_size
    if maximum is not None and not size_at_most(actual.state.template.size, maximum):
        return event
    save_roll, succeeded = resolve_saving_throw(
        actual.state,
        profile.prone_save_ability,
        profile.prone_save_dc,
        dice,
        against_prone=True,
    )
    applied = list(event.applied_condition_ids)
    description = event.description
    if not succeeded and PRONE not in actual.state.active_effect_ids:
        actual.state.active_effect_ids.append(PRONE)
        applied.append(PRONE)
        description += f" {actual.state.template.name} fails the Charge save and is knocked Prone."
    else:
        description += f" {actual.state.template.name} succeeds on the Charge save."
    return event.model_copy(update={
        "saving_throw_roll": save_roll,
        "save_ability": profile.prone_save_ability,
        "save_dc": profile.prone_save_dc,
        "save_succeeded": succeeded,
        "applied_condition_ids": list(dict.fromkeys(applied)),
        "description": description,
    })

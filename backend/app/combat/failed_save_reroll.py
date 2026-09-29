from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.rolls import roll_d20
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import CombatantState, DiceRoll, RollMode, RollRevision
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def _d20_count(mode: RollMode) -> int:
    return 1 if mode is RollMode.NORMAL else 2


def _eligible_sources(
    state: CombatantState,
    roller: EncounterCombatant | None,
    setup: EncounterSetup | None,
) -> list[EncounterCombatant | None]:
    try:
        sources: list[EncounterCombatant | None] = [None]
        if roller is None or setup is None:
            return sources
        allies = setup.heroes if roller.side == "heroes" else setup.monsters
        sources.extend(
            member for member in sorted(allies, key=lambda item: item.combatant_id)
            if member.combatant_id != roller.combatant_id
        )
        return sources
    except Exception as exc:
        logger.exception("Failed to enumerate failed-save reroll sources.")
        raise RuntimeError("Failed-save reroll sources could not be enumerated.") from exc


def _effect_tags(context: SavingThrowContext | None) -> set[str]:
    try:
        tags = set(context.effect_tags if context is not None else ())
        if context is not None and context.condition_id:
            tags.add(context.condition_id.strip().casefold())
        return {item.strip().casefold() for item in tags if item.strip()}
    except Exception as exc:
        logger.exception("Failed to normalize failed-save reroll effect tags.")
        raise RuntimeError("Failed-save reroll effect tags could not be normalized.") from exc


def _replacement_mode(grant, original: DiceRoll) -> RollMode:
    try:
        if grant.reroll_mode == "advantage":
            return RollMode.ADVANTAGE
        if grant.reroll_mode == "disadvantage":
            return RollMode.DISADVANTAGE
        return original.mode
    except Exception as exc:
        logger.exception("Failed to resolve failed-save reroll mode for %s.", grant.source_id)
        raise RuntimeError("Failed-save reroll mode could not be resolved.") from exc


def apply_failed_save_reroll(
    state: CombatantState,
    original: DiceRoll,
    dice: DiceProvider,
    context: SavingThrowContext | None = None,
    *,
    roller: EncounterCombatant | None = None,
    setup: EncounterSetup | None = None,
) -> tuple[DiceRoll, str | None, str | None]:
    """Apply the first legal universal failed-save reroll grant."""
    try:
        tags = _effect_tags(context)
        for source_member in _eligible_sources(state, roller, setup):
            source_state = state if source_member is None else source_member.state
            for grant in source_state.template.progression_features.failed_save_reroll_grants:
                if source_member is not None and grant.target_mode != "self_or_ally":
                    continue
                if source_member is not None:
                    if roller is None or setup is None:
                        continue
                    if combatant_distance(source_member, roller) > grant.range_ft:
                        continue
                required_tags = {item.strip().casefold() for item in grant.required_effect_tags}
                if required_tags and not (required_tags & tags):
                    continue
                if grant.action_cost is not None and not is_available(source_state, grant.action_cost):
                    continue

                resource = None
                if grant.resource_id is not None:
                    resource = next((item for item in source_state.resources if item.id == grant.resource_id), None)
                    if resource is None:
                        raise ValueError(
                            f"Failed-save reroll {grant.source_id} references missing resource {grant.resource_id}."
                        )
                    if resource.current_uses < grant.resource_cost:
                        continue

                d20_count = _d20_count(original.mode)
                retained_bonus_rolls = list(original.rolls[d20_count:])
                replacement_base = roll_d20(
                    dice,
                    original.modifier,
                    _replacement_mode(grant, original),
                )
                replacement_total = replacement_base.total + sum(retained_bonus_rolls)
                replacement_rolls = [*replacement_base.rolls, *retained_bonus_rolls]
                revision = RollRevision(
                    source_effect_id=grant.source_id,
                    kind="full_reroll",
                    original_rolls=list(original.rolls),
                    replacement_rolls=replacement_rolls,
                    original_modifier=original.modifier,
                    replacement_modifier=original.modifier,
                    original_selected=original.selected_roll,
                    replacement_selected=replacement_base.selected_roll,
                    original_total=original.total,
                    replacement_total=replacement_total,
                    accepted="replacement",
                )
                if grant.action_cost is not None:
                    spend(source_state, grant.action_cost)
                if resource is not None:
                    resource.current_uses -= grant.resource_cost
                revised = original.model_copy(update={
                    "notation": f"{original.notation} [{grant.source_name}]",
                    "rolls": replacement_rolls,
                    "selected_roll": replacement_base.selected_roll,
                    "total": replacement_total,
                    "revisions": [*original.revisions, revision],
                })
                return revised, grant.source_id, grant.source_name
        return original, None, None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to apply failed-save reroll for %s.", state.template.name)
        raise RuntimeError("Failed saving-throw reroll could not be resolved.") from exc

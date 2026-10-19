from __future__ import annotations

import logging
from dataclasses import replace

from app.combat.condition_rules import can_see
from app.combat.encounter_targeting import combatant_distance

from app.combat.defensive_modifier_rules import saving_throw_advantage_source_names
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def resolve_repeat_save(target, effect, dice, round_number, setup):
    """Retain semantic save context while refreshing live recipient buffs."""
    try:
        if setup is not None:
            sync_friendly_save_auras(setup)
        context = effect.repeat_save_context or SavingThrowContext(
            condition_id=effect.effect_id, magical_effect=effect.source_is_magical,
        )
        if effect.repeat_save_disadvantage_while_source_visible:
            if setup is None:
                raise ValueError("Source-visible repeat save requires encounter setup.")
            source = next((member for member in [*setup.heroes, *setup.monsters]
                           if member.combatant_id == effect.source_id), None)
            if source is None:
                raise ValueError("Source-visible repeat save cannot locate its original source.")
            if can_see(target.state, source.state, combatant_distance(target, source)):
                context = replace(context, disadvantage_sources=(*context.disadvantage_sources, "visible-source"))
        buffs = saving_throw_advantage_source_names(target.state, effect.repeat_save_ability, context)
        roll, succeeded = resolve_saving_throw(
            target.state, effect.repeat_save_ability, effect.repeat_save_dc, dice, context,
            round_number=round_number, encounter_roller=target, setup=setup,
        )
        return roll, succeeded, buffs
    except Exception:
        logger.exception("Failed repeat save for %s against %s.", target.combatant_id, effect.source_effect_id)
        raise

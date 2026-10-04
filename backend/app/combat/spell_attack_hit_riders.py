from __future__ import annotations

import logging

from app.combat.exile import apply_on_hit_exile
from app.combat.melee_hit_retaliation import apply_melee_hit_retaliation
from app.combat.melee_hit_save_retaliation import apply_melee_hit_save_retaliation
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellAttackAction

logger = logging.getLogger(__name__)


def apply_spell_attack_hit_riders(
    caster: EncounterCombatant,
    target: EncounterCombatant,
    spell: SpellAttackAction,
    setup: EncounterSetup,
    *,
    hit: bool,
    round_number: int,
    turn_key: str,
    dice,
) -> None:
    """Apply shared on-hit riders after a spell attack roll hits."""
    try:
        if not hit or not target.state.is_alive or target.state.is_dead:
            return
        affected = [member.state for member in [*setup.heroes, *setup.monsters]]
        apply_on_hit_exile(
            caster.state,
            target.state,
            None,
            attacker_id=caster.combatant_id,
            round_number=round_number,
            affected_states=affected,
            dice=dice,
            turn_key=turn_key,
        )
        melee = spell.attack_kind == "melee"
        apply_melee_hit_retaliation(
            caster, target, melee=melee, dice=dice, affected_states=affected,
        )
        apply_melee_hit_save_retaliation(
            caster, target, melee=melee, dice=dice, setup=setup,
            round_number=round_number, affected_states=affected,
        )
    except Exception:
        logger.exception("Failed spell-attack hit riders for %s.", caster.combatant_id)
        raise

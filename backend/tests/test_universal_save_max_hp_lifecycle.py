"""Fight-local terminal cleanup for damage-linked maximum-HP save effects."""
from __future__ import annotations

import logging

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_damage import resolve_save_damage
from app.combat.state import build_combatant_state
from app.content.capability_compiler import _compile_save
from app.content.monsters import build_commoner
from app.domain.capability_effects import DiceSpec
from app.domain.capability_save_definitions import SaveCapabilityDefinition
from app.domain.encounters import EncounterCombatant
from app.domain.modifiers import ConcentrationState
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("succeeded,maximum", [(False, 10), (True, 6)])
def test_terminal_maximum_loss_cleans_rage_and_concentration(
    succeeded: bool, maximum: int,
) -> None:
    try:
        # Only shared capability data changes between sources or editions.
        definition = SaveCapabilityDefinition(
            id="synthetic-maximum-drain", name="Renamed Source Action",
            save_ability="constitution", dc=15, range_ft=5,
            damage=DiceSpec(count=2, size=6, bonus=3),
            damage_type=DamageType.PSYCHIC, success_damage="half",
            reduce_hit_point_maximum_on_damage=True, max_hp_zero_kills=True,
        )
        template = build_commoner().model_copy(update={"max_hp": maximum})
        target = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=5,
            state=build_combatant_state(template),
        )
        state = target.state
        state.temporary_hp = 100
        state.active_effect_ids.append("rage")
        state.temporary_damage_resistances.append(DamageType.BLUDGEONING)
        state.concentration = ConcentrationState(
            source_id="source", effect_id="synthetic-concentration",
            started_round=1,
        )
        # Roll 20 lets concentration survive ordinary damage before zero-
        # maximum-HP death, which must still remove it and end Rage.
        resolve_save_damage(
            target, _compile_save(definition),
            FixedDiceProvider([6, 6, 20]), succeeded=succeeded,
            affected_states=[state],
        )
        assert state.is_dead
        assert state.concentration is None
        assert "rage" not in state.active_effect_ids
        assert DamageType.BLUDGEONING not in state.temporary_damage_resistances
        assert state.template.max_hp == maximum  # immutable card
    except Exception:
        logger.exception("Terminal maximum-HP lifecycle regression failed.")
        raise

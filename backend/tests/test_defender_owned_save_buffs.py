from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def _state():
    try:
        source = next(item for item in load_monster_source_2014() if item.id == "satyr")
        template = compile_combatant(adapt_basic_monster_2014(source))
        features = template.progression_features.model_copy(update={
            "saving_throw_advantage_grants": [
                SavingThrowAdvantageGrant(
                    source_id="racial-resilience",
                    source_name="Racial Resilience",
                    abilities=_ABILITIES,
                    against_effect_tags=["poison", "poisoned"],
                )
            ],
        })
        return build_combatant_state(template.model_copy(update={"progression_features": features}))
    except Exception:
        logger.exception("Failed to build defender-owned racial save-buff test state.")
        raise


def test_defender_owned_buff_matches_incoming_damage_semantics() -> None:
    try:
        state = _state()
        roll, _ = resolve_saving_throw(
            state,
            "constitution",
            99,
            FixedDiceProvider([2, 17]),
            SavingThrowContext(effect_tags=frozenset({"poison"})),
        )
        assert roll is not None
        assert roll.mode == "advantage"
        assert roll.rolls == [2, 17]
    except Exception:
        logger.exception("Defender-owned damage-tag save buff regression failed.")
        raise


def test_defender_owned_buff_matches_incoming_condition_semantics() -> None:
    try:
        state = _state()
        roll, _ = resolve_saving_throw(
            state,
            "constitution",
            99,
            FixedDiceProvider([4, 18]),
            SavingThrowContext(
                condition_id="poisoned",
                effect_tags=frozenset({"poisoned"}),
            ),
        )
        assert roll is not None
        assert roll.mode == "advantage"
        assert roll.rolls == [4, 18]
    except Exception:
        logger.exception("Defender-owned condition-tag save buff regression failed.")
        raise


def test_defender_owned_buff_does_not_apply_to_unmatched_effect() -> None:
    try:
        state = _state()
        roll, _ = resolve_saving_throw(
            state,
            "constitution",
            99,
            FixedDiceProvider([11]),
            SavingThrowContext(effect_tags=frozenset({"fire"})),
        )
        assert roll is not None
        assert roll.mode == "normal"
        assert roll.rolls == [11]
    except Exception:
        logger.exception("Unmatched defender-owned save buff regression failed.")
        raise

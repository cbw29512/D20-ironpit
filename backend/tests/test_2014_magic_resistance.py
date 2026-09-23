from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.spell_policy import SpellChoice
from app.combat.spell_resolution import _save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def _satyr_source():
    try:
        return next(monster for monster in load_monster_source_2014() if monster.id == "satyr")
    except Exception:
        logger.exception("Failed to load the 2014 Satyr source record.")
        raise


def _satyr_state():
    try:
        source = _satyr_source()
        return build_combatant_state(compile_combatant(adapt_basic_monster_2014(source)))
    except Exception:
        logger.exception("Failed to build the 2014 Satyr runtime state.")
        raise


def test_magic_resistance_binds_as_contextual_save_advantage() -> None:
    try:
        source = _satyr_source()
        assert unsupported_traits_2014(source) == ()
        assert basic_blockers_2014(source) == ()

        template = compile_combatant(adapt_basic_monster_2014(source))
        grants = template.progression_features.saving_throw_advantage_grants
        assert len(grants) == 1
        assert grants[0].source_name == "Magic Resistance"
        assert grants[0].requires_magical_effect is True
        assert set(grants[0].abilities) == {
            "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
        }
    except Exception:
        logger.exception("2014 Magic Resistance source binding regression failed.")
        raise


def test_magic_resistance_applies_only_to_magical_effect_saves() -> None:
    try:
        magical = _satyr_state()
        roll, _ = resolve_saving_throw(
            magical,
            "wisdom",
            99,
            FixedDiceProvider([2, 17]),
            SavingThrowContext(magical_effect=True),
        )
        assert roll is not None
        assert roll.mode == "advantage"
        assert roll.rolls == [2, 17]

        nonmagical = _satyr_state()
        roll, _ = resolve_saving_throw(
            nonmagical,
            "wisdom",
            99,
            FixedDiceProvider([10]),
            SavingThrowContext(magical_effect=False),
        )
        assert roll is not None
        assert roll.mode == "normal"
        assert roll.rolls == [10]
    except Exception:
        logger.exception("Contextual Magic Resistance saving-throw regression failed.")
        raise


def test_spell_save_conversion_marks_the_effect_magical() -> None:
    try:
        spell = SpellSaveAction(
            id="test-spell",
            name="Test Spell",
            level=0,
            range_ft=60,
            save_ability="wisdom",
            dc=12,
        )
        action = _save_action(SpellChoice(spell, 0, ("target",)))
        assert action.magical_effect is True
    except Exception:
        logger.exception("Spell saving-throw magical-context regression failed.")
        raise

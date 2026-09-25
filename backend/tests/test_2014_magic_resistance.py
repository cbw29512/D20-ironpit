from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.saving_throws import resolve_save_action
from app.combat.spell_policy import SpellChoice
from app.combat.spell_resolution import _save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant
from app.domain.progression import SavingThrowAdvantageGrant
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


def test_magic_resistance_source_name_is_preserved_in_save_log() -> None:
    try:
        actor = EncounterCombatant(
            combatant_id="actor",
            side="heroes",
            position_ft=0,
            state=_satyr_state(),
        )
        target = EncounterCombatant(
            combatant_id="target",
            side="monsters",
            position_ft=5,
            state=_satyr_state(),
        )
        action = SavingThrowAction(
            id="magical-test",
            name="Magical Test",
            save_ability="wisdom",
            dc=40,
            range_ft=60,
            magical_effect=True,
        )
        event = resolve_save_action(
            1, 1, actor, target, action, 5, FixedDiceProvider([2, 17]),
        )
        assert event.saving_throw_roll is not None
        assert event.saving_throw_roll.mode == "advantage"
        assert "Magic Resistance grants Advantage on the save." in event.description
    except Exception:
        logger.exception("Magic Resistance combat-log source regression failed.")
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


def test_effect_tag_save_advantage_is_contextual_and_composes() -> None:
    try:
        state = _satyr_state()
        state.template.progression_features.saving_throw_advantage_grants.append(
            SavingThrowAdvantageGrant(
                source_id="poison-resilience",
                source_name="Poison Resilience",
                abilities=["wisdom"],
                required_effect_tags=["poison"],
            )
        )
        from app.combat.opening_modifiers import opening_modifiers
        state.active_modifiers = opening_modifiers(state.template)

        poison_roll, _ = resolve_saving_throw(
            state,
            "wisdom",
            99,
            FixedDiceProvider([3, 18]),
            SavingThrowContext(
                magical_effect=True,
                effect_tags=frozenset({"poison"}),
            ),
        )
        assert poison_roll is not None
        assert poison_roll.mode == "advantage"
        assert poison_roll.rolls == [3, 18]

        from app.combat.defensive_modifier_rules import saving_throw_advantage_source_names
        assert saving_throw_advantage_source_names(
            state,
            "wisdom",
            SavingThrowContext(
                magical_effect=True,
                effect_tags=frozenset({"poison"}),
            ),
        ) == ["Magic Resistance", "Poison Resilience"]

        ordinary = _satyr_state()
        ordinary.template.progression_features.saving_throw_advantage_grants.append(
            SavingThrowAdvantageGrant(
                source_id="poison-resilience",
                source_name="Poison Resilience",
                abilities=["wisdom"],
                required_effect_tags=["poison"],
            )
        )
        ordinary.active_modifiers = opening_modifiers(ordinary.template)
        ordinary_roll, _ = resolve_saving_throw(
            ordinary,
            "wisdom",
            99,
            FixedDiceProvider([11]),
            SavingThrowContext(),
        )
        assert ordinary_roll is not None
        assert ordinary_roll.mode == "normal"
        assert ordinary_roll.rolls == [11]
    except Exception:
        logger.exception("Semantic save-effect tag regression failed.")
        raise


def test_poison_damage_save_action_supplies_poison_effect_tag() -> None:
    try:
        actor = EncounterCombatant(
            combatant_id="actor-poison",
            side="heroes",
            position_ft=0,
            state=_satyr_state(),
        )
        target = EncounterCombatant(
            combatant_id="target-poison",
            side="monsters",
            position_ft=5,
            state=_satyr_state(),
        )
        target.state.template.progression_features.saving_throw_advantage_grants.append(
            SavingThrowAdvantageGrant(
                source_id="poison-resilience",
                source_name="Poison Resilience",
                abilities=["constitution"],
                required_effect_tags=["poison"],
            )
        )
        from app.combat.opening_modifiers import opening_modifiers
        target.state.active_modifiers = opening_modifiers(target.state.template)

        action = SavingThrowAction(
            id="poison-test",
            name="Poison Test",
            save_ability="constitution",
            dc=40,
            range_ft=60,
            damage_dice_count=1,
            damage_dice_size=6,
            damage_type="poison",
        )
        event = resolve_save_action(
            1, 1, actor, target, action, 5, FixedDiceProvider([2, 17, 4]),
        )
        assert event.saving_throw_roll is not None
        assert event.saving_throw_roll.mode == "advantage"
        assert "Poison Resilience grants Advantage on the save." in event.description
    except Exception:
        logger.exception("Poison save-action semantic tag regression failed.")
        raise

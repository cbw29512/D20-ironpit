from __future__ import annotations

import logging

from app.combat.spell_choice import SpellChoice
from app.combat.spell_save_effect_resolution import compile_spell_save_action
from app.content.shared_control_spells_2014 import hold_monster_2014

logger = logging.getLogger(__name__)


def test_hold_monster_2014_declares_exact_base_spell_semantics() -> None:
    try:
        spell = hold_monster_2014(21)

        assert spell.id == "hold-monster"
        assert spell.level == 5
        assert spell.action_cost == "action"
        assert spell.range_ft == 90
        assert spell.requires_target_sight is True
        assert spell.save_ability == "wisdom"
        assert spell.dc == 21
        assert spell.excluded_target_creature_types == ["undead"]
        assert spell.concentration is True
        assert spell.duration_minutes == 1

        effect = spell.failed_save_timed_effect
        assert effect is not None
        assert effect.effect_id == "paralyzed"
        assert effect.duration_rounds == 10
        assert effect.repeat_save_ability == "wisdom"
        assert effect.repeat_save_dc == 21
        assert effect.repeat_save_timing == "target_turn_end"
    except Exception:
        logger.exception("2014 Hold Monster declaration regression failed.")
        raise


def test_hold_monster_compiles_to_shared_saving_throw_action() -> None:
    try:
        spell = hold_monster_2014(17)
        action = compile_spell_save_action(
            SpellChoice(spell, 5, ("renamed-target",))
        )

        assert action.id == "hold-monster"
        assert action.name == "Hold Monster"
        assert action.range_ft == 90
        assert action.requires_target_sight is True
        assert action.save_ability == "wisdom"
        assert action.dc == 17
        assert action.excluded_target_creature_types == ["undead"]
        assert action.failed_save_timed_effect is not None
        assert action.failed_save_timed_effect.effect_id == "paralyzed"
        assert action.failed_save_timed_effect.repeat_save_timing == "target_turn_end"
    except Exception:
        logger.exception("2014 Hold Monster shared-action compilation regression failed.")
        raise


def test_hold_monster_builder_is_parameterized_not_source_identity_keyed() -> None:
    try:
        low = hold_monster_2014(12)
        high = hold_monster_2014(21)

        assert low.dc == 12
        assert high.dc == 21
        assert low.failed_save_timed_effect is not None
        assert high.failed_save_timed_effect is not None
        assert low.failed_save_timed_effect.repeat_save_dc == 12
        assert high.failed_save_timed_effect.repeat_save_dc == 21
    except Exception:
        logger.exception("2014 Hold Monster parameterization regression failed.")
        raise

"""Pairwise target geometry is a reusable spell-data qualification."""
from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

from app.combat.spell_target_groups import (
    choose_spell_target_group, target_group_within_distance,
)
from app.content.monster_command_spell_2014 import command_grovel_2014

logger = logging.getLogger(__name__)


def _actor(name: str, position: int):
    try:
        return SimpleNamespace(
            combatant_id=name, position_ft=position,
            state=SimpleNamespace(position=None),
        )
    except Exception:
        logger.exception("Failed to build synthetic spell target.")
        raise


def test_universal_group_chooses_largest_legal_pairwise_cluster() -> None:
    try:
        a, b, c, d = (
            _actor("a", 0), _actor("b", 20), _actor("c", 45), _actor("d", 75),
        )
        assert target_group_within_distance([a, b], 30)
        assert not target_group_within_distance([a, c], 30)
        assert not target_group_within_distance([a, b, c], 30)
        assert choose_spell_target_group([a, c, b, d], 3, 30) == [a, b]
        assert choose_spell_target_group([a, c, b, d], 2, None) == [a, c]
        assert choose_spell_target_group([a, c, b, d], 1, 30) == [a]
        assert choose_spell_target_group([], 3, 30) == []
        with pytest.raises(ValueError):
            choose_spell_target_group([a], 0, 30)
        # No target may be over the declared pairwise distance.
        for limit in (5, 15, 30):
            selected = choose_spell_target_group([a, c, b, d], 4, limit)
            assert target_group_within_distance(selected, limit)
    except Exception:
        logger.exception("Universal spell group target selection regressed.")
        raise


def test_command_source_data_sets_30_foot_pair_distance_and_rejects_area_mixing() -> None:
    try:
        command = command_grovel_2014(11)
        assert command.max_target_pair_distance_ft == 30
        with pytest.raises(ValueError, match="Target-group distance"):
            command.model_copy(update={"area_radius_ft": 10}).model_validate(
                {**command.model_dump(), "area_radius_ft": 10},
            )
    except Exception:
        logger.exception("Source-owned target-group geometry schema regressed.")
        raise


def test_spell_effect_direct_resolution_rejects_illegal_group_without_state_mutation() -> None:
    try:
        from app.combat.spell_choice import SpellChoice
        from app.combat.spell_save_effect_resolution import resolve_spell_save_effect
        from app.combat.state import build_combatant_state
        from app.content.audited_fighter import build_karnok_stoneward
        from app.domain.encounters import EncounterCombatant, EncounterSetup

        template = build_karnok_stoneward()
        caster = EncounterCombatant(
            combatant_id="caster", side="monsters", position_ft=15,
            state=build_combatant_state(template),
        )
        targets = [
            EncounterCombatant(
                combatant_id=f"target-{i}", side="heroes", position_ft=pos,
                state=build_combatant_state(template),
            )
            for i, pos in enumerate((0, 40))
        ]
        setup = EncounterSetup(
            heroes=targets, monsters=[caster], hero_total_levels=1, monster_total_cr="1",
        )
        before = [member.state.model_dump() for member in [caster, *targets]]
        action = command_grovel_2014(11)
        choice = SpellChoice(
            action=action, slot_level=2,
            target_ids=tuple(target.combatant_id for target in targets),
        )
        with pytest.raises(RuntimeError, match="Save-spell effect could not be resolved") as err:
            resolve_spell_save_effect(
                1, 1, caster, setup, choice, "1:caster", object(),
            )
        assert isinstance(err.value.__cause__, ValueError)
        assert "pairwise distance" in str(err.value.__cause__)
        assert [member.state.model_dump() for member in [caster, *targets]] == before
    except Exception:
        logger.exception("Illegal direct spell target group mutated fight state.")
        raise

"""2014 Mummy Dreadful Glare source binding and universal save lifecycle."""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_dreadful_glare_2014 import source_proven_dreadful_glare_2014
from app.domain.encounters import EncounterCombatant
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


def _source(monster_id: str):
    try:
        return next(item for item in load_monster_source_2014() if item.id == monster_id)
    except Exception:
        logger.exception("Failed to load 2014 source %s.", monster_id)
        raise


def _monster(monster_id: str, combatant_id: str) -> EncounterCombatant:
    try:
        template = compile_combatant(adapt_basic_monster_2014(_source(monster_id)))
        state = build_combatant_state(template)
        state.position = GridPosition(x=2, y=0)
        return EncounterCombatant(
            combatant_id=combatant_id, side="monsters", position_ft=10, state=state,
        )
    except Exception:
        logger.exception("Failed to compile 2014 monster %s.", monster_id)
        raise


def _target() -> EncounterCombatant:
    try:
        template = build_karnok_stoneward().model_copy(deep=True)
        saves = dict(template.saving_throw_bonuses)
        saves["wisdom"] = 0
        template = template.model_copy(update={"saving_throw_bonuses": saves})
        state = build_combatant_state(template)
        state.position = GridPosition(x=4, y=0)
        return EncounterCombatant(
            combatant_id="hero:test", side="heroes", position_ft=20, state=state,
        )
    except Exception:
        logger.exception("Failed to build Dreadful Glare target.")
        raise


def _glare(member: EncounterCombatant):
    try:
        return next(
            action for action in member.state.template.saving_throw_actions
            if action.id == "dreadful-glare"
        )
    except Exception:
        logger.exception("Dreadful Glare was not compiled.")
        raise


def test_source_proves_both_dreadful_glare_variants() -> None:
    mummy, = source_proven_dreadful_glare_2014(_source("mummy"))
    lord, = source_proven_dreadful_glare_2014(_source("mummy-lord"))
    assert (mummy.dc, mummy.range_ft) == (11, 60)
    assert (lord.dc, lord.range_ft) == (16, 60)
    assert mummy.requires_target_sight and mummy.requires_target_to_see_source
    assert lord.requires_target_sight and lord.requires_target_to_see_source
    assert mummy.failed_save_timed_effect.failure_margin_escalation.margin == 5
    assert lord.failed_save_timed_effect.failure_margin_escalation.margin == 5


def test_fail_by_less_than_five_is_frightened_only() -> None:
    mummy, target = _monster("mummy", "mummy:a"), _target()
    event = resolve_save_action(
        1, 1, mummy, target, _glare(mummy), 10, FixedDiceProvider([8]),
    )
    assert event.save_succeeded is False
    assert event.applied_condition_ids == ["frightened"]
    assert "paralyzed" not in target.state.active_effect_ids


def test_fail_by_five_adds_paralyzed_for_same_lifecycle() -> None:
    mummy, target = _monster("mummy", "mummy:a"), _target()
    event = resolve_save_action(
        1, 1, mummy, target, _glare(mummy), 10, FixedDiceProvider([6]),
    )
    assert event.applied_condition_ids == ["frightened", "paralyzed"]
    assert {"frightened", "paralyzed"} <= set(target.state.active_effect_ids)
    owners = [item for item in target.state.timed_effects if item.source_effect_id == "dreadful-glare"]
    assert len(owners) == 2
    assert owners[0].expires_round == 2


def test_success_immunity_scope_matches_printed_mummy_families() -> None:
    first = _monster("mummy", "mummy:a")
    second = _monster("mummy", "mummy:b")
    lord = _monster("mummy-lord", "mummy-lord:a")
    target = _target()
    action = _glare(first)
    event = resolve_save_action(1, 1, first, target, action, 10, FixedDiceProvider([20]))
    assert event.save_succeeded is True
    assert not legal_save_action(_glare(second), target, 10, second.combatant_id, second)
    assert legal_save_action(_glare(lord), target, 10, lord.combatant_id, lord)

    target = _target()
    event = resolve_save_action(2, 1, lord, target, _glare(lord), 10, FixedDiceProvider([20]))
    assert event.save_succeeded is True
    assert not legal_save_action(_glare(second), target, 10, second.combatant_id, second)
    assert not legal_save_action(_glare(lord), target, 10, lord.combatant_id, lord)


def test_mutated_source_fails_closed() -> None:
    source = _source("mummy")
    altered = source.model_copy(
        update={"source_actions": source.source_actions.replace("by 5 or more", "by 4 or more")}
    )
    assert source_proven_dreadful_glare_2014(altered) == []

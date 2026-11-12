"""Real save-action combat confirms shared source-type capacities and harm saves."""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.source_bound_effects import (cleanup_disabled_source_effects, resolve_damage_repeat_saves)
from app.combat.source_damage_repeat_eligibility import damage_triggers_repeat_save
from app.combat.source_effect_immunity import has_source_effect_immunity
from app.combat.state import build_combatant_state
from app.content.capability_compiler import _compile_save
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_fey_charm_2014 import source_proven_fey_charm_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _encounter():
    try:
        card = next(c for c in load_monster_source_2014()
                    if c.id == "dryad")
        action = _compile_save(source_proven_fey_charm_2014(card)[0])
        owner = EncounterCombatant(
            combatant_id="fey-owner", side="monsters", position_ft=0,
            state=build_combatant_state(build_goblin_warrior()),
        )
        ally = EncounterCombatant(
            combatant_id="fey-ally", side="monsters", position_ft=0,
            state=build_combatant_state(build_goblin_warrior()),
        )
        targets = []
        for kind, count in (("humanoid", 2), ("beast", 4)):
            for index in range(count):
                base = build_demo_fighter().model_copy(update={"creature_type": kind})
                targets.append(EncounterCombatant(
                    combatant_id=f"{kind}-{index}", side="heroes", position_ft=5,
                    state=build_combatant_state(base),
                ))
        setup = EncounterSetup(
            heroes=targets, monsters=[owner, ally], ruleset="2014",
            hero_total_levels=6, monster_total_cr="1",
        )
        return card, owner, ally, targets, setup, action
    except Exception:
        logger.exception("Failed 2014 real Fey Charm encounter setup.")
        raise


def _cast(owner, target, setup, action):
    try:
        return resolve_save_action(
            1, 1, owner, target, action, 5, FixedDiceProvider([1]),
            spend_action=False, check_resource=False, spend_resource=False,
            setup=setup,
            affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
        )
    except Exception:
        logger.exception("Failed Fey Charm save against %s.", target.combatant_id)
        raise


def _owned(target, owner, action):
    return [e for e in target.state.timed_effects
            if e.effect_id == "charmed" and e.source_id == owner.combatant_id
            and e.source_effect_id == action.id]


def test_fey_charm_uses_independent_humanoid_and_beast_capacities():
    try:
        source, owner, ally, targets, setup, charm = _encounter()
        human1, human2, beast1, beast2, beast3, beast4 = targets
        before = source.model_dump_json()
        for target in (human1, beast1, beast2, beast3, human2):
            event = _cast(owner, target, setup, charm)
            assert "charmed" in event.applied_condition_ids
        assert not _owned(human1, owner, charm)
        assert not has_source_effect_immunity(human1.state, charm.id, owner.combatant_id)
        assert _owned(human2, owner, charm)
        assert all(_owned(x, owner, charm) for x in (beast1, beast2, beast3))
        _cast(owner, beast4, setup, charm)
        assert not _owned(beast1, owner, charm)
        assert not has_source_effect_immunity(beast1.state, charm.id, owner.combatant_id)
        assert all(_owned(x, owner, charm) for x in (beast2, beast3, beast4))
        assert _owned(human2, owner, charm)
        assert human2.side == "heroes" and human2.state.controlled_by is None
        assert source.model_dump_json() == before
    except Exception:
        logger.exception("Independent type-specific Fey Charm capacities regressed.")
        raise


def test_fey_charm_harm_repeat_only_when_source_side_damages_target():
    try:
        _source, owner, ally, targets, setup, charm = _encounter()
        victim = targets[0]
        _cast(owner, victim, setup, charm)
        effect = _owned(victim, owner, charm)[0]
        assert damage_triggers_repeat_save(effect, owner, setup)
        assert damage_triggers_repeat_save(effect, ally, setup)
        assert not damage_triggers_repeat_save(effect, targets[1], setup)
        untouched, index = resolve_damage_repeat_saves(
            2, 1, targets[1], victim, setup, FixedDiceProvider([20]),
        )
        assert untouched == [] and index == 2
        events, index = resolve_damage_repeat_saves(
            2, 1, ally, victim, setup, FixedDiceProvider([20]),
        )
        assert len(events) == 1 and index == 3
        assert events[0].save_succeeded and events[0].feature_id == "fey-charm"
        assert not _owned(victim, owner, charm)
        assert has_source_effect_immunity(victim.state, charm.id, owner.combatant_id)
    except Exception:
        logger.exception("Fey Charm source-side damage repeat save failed.")
        raise


def test_fey_charm_owner_death_does_not_grant_success_immunity():
    try:
        _source, owner, _ally, targets, setup, charm = _encounter()
        victim = targets[0]
        _cast(owner, victim, setup, charm)
        assert _owned(victim, owner, charm)
        owner.state.current_hp = 0
        cleanup_disabled_source_effects(setup)
        assert not _owned(victim, owner, charm)
        assert not has_source_effect_immunity(
            victim.state, charm.id, owner.combatant_id,
        )
    except Exception:
        logger.exception("Owner death should end Fey Charm without successful-save immunity.")
        raise

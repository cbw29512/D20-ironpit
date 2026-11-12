"""Real 2014 printed Charm Action uses the generic encounter save pipeline."""
from __future__ import annotations

import logging

from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.damage_reaction_events import (
    applied_damage_total, resolve_damage_event_reactions,
)
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.saving_throw_legality import legal_save_action
from app.combat.saving_throws import resolve_save_action
from app.combat.source_effect_immunity import has_source_effect_immunity
from app.combat.state import build_combatant_state
from app.content.capability_compiler import _compile_save
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_charm_control_2014 import source_proven_charm_control_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _fight():
    try:
        card = next(x for x in load_monster_source_2014()
                    if source_proven_charm_control_2014(x))
        (ability,) = source_proven_charm_control_2014(card)
        owner = EncounterCombatant(
            combatant_id="charm-owner", side="monsters", position_ft=0,
            state=build_combatant_state(
                build_goblin_warrior().model_copy(update={"name": "Renamed Actor"}),
            ),
        )
        targets = [
            EncounterCombatant(
                combatant_id=f"target-{i}", side="heroes", position_ft=5,
                state=build_combatant_state(build_demo_fighter().model_copy(update={"creature_type": "humanoid"})),
            ) for i in range(2)
        ]
        setup = EncounterSetup(
            heroes=targets, monsters=[owner], ruleset="2014",
            hero_total_levels=2, monster_total_cr="1/4",
        )
        return card, owner, targets, setup, _compile_save(ability)
    except Exception:
        logger.exception("2014 source Charm combat setup failed.")
        raise


def _cast(owner, target, setup, action, die=1):
    try:
        return resolve_save_action(
            1, 1, owner, target, action, 5, FixedDiceProvider([die]),
            spend_action=False, check_resource=False, spend_resource=False,
            setup=setup,
            affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
        )
    except Exception:
        logger.exception("2014 source Charm resolution failed against %s.",
                         target.combatant_id)
        raise


def test_source_charm_timed_target_cap_damage_repeat_and_immunity():
    try:
        card, owner, (first, second), setup, charm = _fight()
        before = card.model_dump_json()
        assert legal_save_action(charm, first, 5, owner.combatant_id, owner)
        event = _cast(owner, first, setup, charm)
        assert event.feature_id == "charm" and "Charm" in event.description
        assert event.applied_condition_ids == ["charmed"]
        # This is not Possession or a side swap: only the Charmed condition
        # and its existing targeting gate affect the target in Iron Pit.
        assert first.state.controlled_by is None
        assert owner.state.controlling_target_ids == []
        assert first.side == "heroes"
        instance = next(x for x in first.state.timed_effects
                        if x.effect_id == "charmed")
        assert instance.repeat_save_timing is None
        assert instance.damage_repeat_save_trigger == "any_damage_source"
        assert instance.expires_round == 14401
        for timing in ("target_turn_start", "target_turn_end"):
            events, _ = resolve_target_condition_timing(
                2, 1, first, timing, FixedDiceProvider([20]), setup,
            )
            assert not any(e.event_type == "saving_throw" for e in events)
        _cast(owner, second, setup, charm)
        assert not any(e.source_effect_id == "charm" and e.effect_id == "charmed"
                       for e in first.state.timed_effects)
        assert has_source_effect_immunity(first.state, charm.id, owner.combatant_id)
        assert not legal_save_action(charm, first, 5, owner.combatant_id, owner)
        assert any(e.effect_id == "charmed" and e.source_id == owner.combatant_id
                   for e in second.state.timed_effects)
        hit = resolve_encounter_attack(
            3, 1, owner, second, owner.state.template.weapon_attack, 5,
            FixedDiceProvider([19, 4]), setup, spend_action=False,
        )
        assert applied_damage_total(hit) > 0
        triggered, _ = resolve_damage_event_reactions(
            4, 1, owner, hit, setup, FixedDiceProvider([20]),
        )
        assert len(triggered) == 1 and triggered[0].feature_id == "charm"
        assert triggered[0].save_succeeded
        assert has_source_effect_immunity(second.state, charm.id, owner.combatant_id)
        assert card.model_dump_json() == before
    except Exception:
        logger.exception("2014 Charm real combat transition failed.")
        raise


def test_source_charm_uses_generic_sight_and_range_target_gate():
    try:
        _card, owner, (target, _), setup, charm = _fight()
        assert not legal_save_action(charm, target, 35, owner.combatant_id, owner)
        # The printed Charm only targets humanoids. Renamed, nonhumanoid
        # synthetic combatants use the same generic creature-type gate.
        construct = EncounterCombatant(
            combatant_id="construct", side="heroes", position_ft=5,
            state=build_combatant_state(
                build_demo_fighter().model_copy(update={"creature_type": "construct"}),
            ),
        )
        assert not legal_save_action(
            charm, construct, 5, owner.combatant_id, owner,
        )
        owner.state.active_effect_ids.append("blinded")
        assert not legal_save_action(charm, target, 5, owner.combatant_id, owner)
        owner.state.active_effect_ids.remove("blinded")
        assert legal_save_action(charm, target, 5, owner.combatant_id, owner)
    except Exception:
        logger.exception("2014 Charm source sight/range gate failed.")
        raise

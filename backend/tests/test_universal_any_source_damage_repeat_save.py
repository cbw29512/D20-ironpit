"""Source-neutral repeat saves after damage from an effect owner or anyone else."""
from __future__ import annotations

import logging

import pytest
from pydantic import ValidationError

from app.combat.damage_reaction_events import (
    applied_damage_total, resolve_damage_event_reactions,
)
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)


def _member(identity, side, template):
    try:
        return EncounterCombatant(
            combatant_id=identity, side=side, position_ft=5,
            state=build_combatant_state(template),
        )
    except Exception:
        logger.exception("Failed preparing damage-repeat fixture %s.", identity)
        raise


@pytest.mark.parametrize("owner_deals_damage", [True, False])
def test_any_source_damage_triggers_one_repeat_save(owner_deals_damage: bool):
    try:
        target = _member("hero", "heroes", build_demo_fighter())
        owner = _member("source-owner", "monsters", build_goblin_warrior())
        other = _member("other-attacker", "monsters", build_goblin_warrior())
        attacker = owner if owner_deals_damage else other
        setup = EncounterSetup(
            heroes=[target], monsters=[owner, other],
            hero_total_levels=1, monster_total_cr="1/4",
        )
        assert apply_timed_condition(
            target.state, "charmed", owner.combatant_id,
            source_effect_id="renamed-control",
            applied_round=1, expiry_timing="target_turn_end",
            repeat_save_ability="wisdom", repeat_save_dc=10,
            repeat_save_timing="target_turn_end",
            damage_repeat_save_trigger="any_damage_source",
            use_default_poison_recovery=False,
        ) == "charmed"
        event = resolve_encounter_attack(
            1, 1, attacker, target, attacker.state.template.weapon_attack,
            5, FixedDiceProvider([19, 4]), setup, spend_action=False,
        )
        assert applied_damage_total(event) > 0
        followups, sequence = resolve_damage_event_reactions(
            2, 1, attacker, event, setup, FixedDiceProvider([20]),
        )
        assert [x.event_type for x in followups] == ["saving_throw"]
        assert followups[0].feature_id == "renamed-control"
        assert followups[0].save_succeeded
        assert "charmed" not in target.state.active_effect_ids
        assert sequence == 3
    except Exception:
        logger.exception("Damage-based repeat save failed, owner=%s.", owner_deals_damage)
        raise


def test_no_damage_does_not_trigger_source_owned_repeat_save():
    try:
        target = _member(
            "untouched", "heroes",
            build_demo_fighter().model_copy(update={"armor_class": 99}),
        )
        source = _member("owner", "monsters", build_goblin_warrior())
        setup = EncounterSetup(
            heroes=[target], monsters=[source],
            hero_total_levels=1, monster_total_cr="1/4",
        )
        apply_timed_condition(
            target.state, "charmed", source.combatant_id,
            source_effect_id="another-label",
            repeat_save_ability="wisdom", repeat_save_dc=10,
            repeat_save_timing="target_turn_end",
            damage_repeat_save_trigger="any_damage_source",
            use_default_poison_recovery=False,
        )
        miss = resolve_encounter_attack(
            1, 1, source, target, source.state.template.weapon_attack, 5,
            FixedDiceProvider([19]), setup, spend_action=False,
        )
        assert applied_damage_total(miss) == 0
        followups, seq = resolve_damage_event_reactions(
            2, 1, source, miss, setup, FixedDiceProvider([20]),
        )
        assert followups == [] and seq == 2
        assert "charmed" in target.state.active_effect_ids
    except Exception:
        logger.exception("No-damage repeat-save guard failed.")
        raise


def test_any_source_requires_complete_repeat_save_fields():
    try:
        rider = FailedSaveTimedEffect(
            effect_id="charmed", repeat_save_ability="wisdom",
            repeat_save_dc=15, repeat_save_timing="target_turn_end",
            damage_repeat_save_trigger="any_damage_source",
        )
        assert rider.damage_repeat_save_trigger == "any_damage_source"
        with pytest.raises(ValidationError):
            FailedSaveTimedEffect(
                effect_id="charmed", damage_repeat_save_trigger="any_damage_source",
            )
    except Exception:
        logger.exception("Repeat-save schema guard failed.")
        raise

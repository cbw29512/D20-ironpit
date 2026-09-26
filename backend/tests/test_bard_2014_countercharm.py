from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.dice import FixedDiceProvider
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.saving_throw_rolls import resolve_saving_throw, saving_throw_mode
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.bard_2014_countercharm import countercharm_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode
from app.domain.saving_throw_context import SavingThrowContext


def _member(combatant_id: str, side: str, position: int, *, countercharm: bool = False):
    template = build_commoner().model_copy(update={
        "id": f"{combatant_id}-template",
        "name": combatant_id.title(),
        "ruleset": "2014",
        "timed_self_buff_actions": [countercharm_2014()] if countercharm else [],
    })
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup():
    bard = _member("bard", "heroes", 0, countercharm=True)
    ally = _member("ally", "heroes", 20)
    enemy = _member("enemy", "monsters", 40)
    setup = EncounterSetup(
        heroes=[bard, ally],
        monsters=[enemy],
        hero_total_levels=2,
        monster_total_cr="0",
        ruleset="2014",
    )
    return setup, bard, ally


def test_countercharm_is_at_will_and_uses_source_turn_end_lifecycle() -> None:
    action = countercharm_2014()
    assert action.resource_id is None
    assert action.action_cost == "action"
    assert action.duration_rounds == 1
    assert action.expiry_timing == "source_turn_end"
    assert action.ends_if_source_incapacitated is True
    assert action.ends_if_source_dead is True
    assert action.friendly_save_advantage_aura is not None
    assert action.friendly_save_advantage_aura.radius_ft == 30
    assert action.friendly_save_advantage_aura.requires_hearing is True
    assert set(action.friendly_save_advantage_aura.required_effect_tags) == {"charmed", "frightened"}


def test_countercharm_live_aura_grants_only_matching_save_advantage() -> None:
    setup, bard, ally = _setup()
    event = resolve_timed_self_buff(1, 1, bard, countercharm_2014())
    assert event.feature_id == "countercharm"
    assert event.resource_remaining is None
    assert is_available(bard.state, "action") is False

    sync_friendly_save_auras(setup)
    assert saving_throw_mode(
        ally.state, "wisdom", SavingThrowContext(effect_tags=frozenset({"charmed"})),
    ) is RollMode.ADVANTAGE
    assert saving_throw_mode(
        ally.state, "wisdom", SavingThrowContext(effect_tags=frozenset({"frightened"})),
    ) is RollMode.ADVANTAGE
    assert saving_throw_mode(
        ally.state, "wisdom", SavingThrowContext(effect_tags=frozenset({"poison"})),
    ) is RollMode.NORMAL

    roll, _ = resolve_saving_throw(
        ally.state,
        "wisdom",
        99,
        FixedDiceProvider([4, 17]),
        SavingThrowContext(effect_tags=frozenset({"charmed"})),
    )
    assert roll is not None
    assert roll.mode is RollMode.ADVANTAGE
    assert roll.selected_roll == 17


def test_countercharm_recalculates_range_hearing_and_source_activity() -> None:
    setup, bard, ally = _setup()
    resolve_timed_self_buff(1, 1, bard, countercharm_2014())

    sync_friendly_save_auras(setup)
    context = SavingThrowContext(effect_tags=frozenset({"charmed"}))
    assert saving_throw_mode(ally.state, "wisdom", context) is RollMode.ADVANTAGE

    ally.position_ft = 35
    sync_friendly_save_auras(setup)
    assert saving_throw_mode(ally.state, "wisdom", context) is RollMode.NORMAL

    ally.position_ft = 20
    apply_timed_condition(
        ally.state, "deafened", "enemy", applied_round=1, expires_round=3,
        expiry_timing="source_turn_end", use_default_poison_recovery=False,
    )
    sync_friendly_save_auras(setup)
    assert saving_throw_mode(ally.state, "wisdom", context) is RollMode.NORMAL

    ally.state.timed_effects.clear()
    ally.state.active_effect_ids.clear()
    apply_timed_condition(
        bard.state, "incapacitated", "enemy", applied_round=1, expires_round=3,
        expiry_timing="source_turn_end", use_default_poison_recovery=False,
    )
    sync_friendly_save_auras(setup)
    assert saving_throw_mode(ally.state, "wisdom", context) is RollMode.NORMAL

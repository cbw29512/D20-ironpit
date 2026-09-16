from app.combat.charge import resolve_charge_closing
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _template(monster_id: str):
    return next(item for item in build_basic_2014_monsters() if item.id == monster_id)


def _opening_pair():
    attacker = EncounterCombatant(
        combatant_id="monster:allosaurus", side="monsters", position_ft=5,
        state=build_combatant_state(_template("2014-allosaurus")),
    )
    target = EncounterCombatant(
        combatant_id="hero:bandit", side="heroes", position_ft=0,
        state=build_combatant_state(_template("2014-bandit")),
    )
    attacker.state.initiative_total = 20
    target.state.initiative_total = 10
    begin_turn(attacker.state)
    setup = EncounterSetup(
        heroes=[target], monsters=[attacker], hero_total_levels=1, monster_total_cr="2",
    )
    return attacker, target, setup


def _attack_ids(events):
    return [event.weapon_id for event in events if event.event_type == "attack"]


def test_2014_pounce_save_success_blocks_follow_up_bite() -> None:
    attacker, target, setup = _opening_pair()
    events, sequence, handled = resolve_charge_closing(
        1, 1, attacker, target, FixedDiceProvider([15, 1, 15]), setup,
    )
    assert handled is True and sequence == 2
    assert _attack_ids(events) == ["2014-allosaurus-claw"]
    assert "prone" not in target.state.active_effect_ids
    assert attacker.state.bonus_action_available is True


def test_2014_pounce_failed_save_grants_and_spends_bonus_action_bite() -> None:
    attacker, target, setup = _opening_pair()
    events, sequence, handled = resolve_charge_closing(
        1, 1, attacker, target, FixedDiceProvider([15, 1, 1, 15, 1, 1]), setup,
    )
    assert handled is True and sequence == 3
    assert _attack_ids(events) == ["2014-allosaurus-claw", "2014-allosaurus-bite"]
    assert "prone" in target.state.active_effect_ids
    assert attacker.state.bonus_action_available is False


def test_2014_pounce_requires_available_bonus_action() -> None:
    attacker, target, setup = _opening_pair()
    attacker.state.bonus_action_available = False
    events, sequence, handled = resolve_charge_closing(
        1, 1, attacker, target, FixedDiceProvider([15, 1, 1]), setup,
    )
    assert handled is True and sequence == 2
    assert _attack_ids(events) == ["2014-allosaurus-claw"]
    assert "prone" in target.state.active_effect_ids
    assert attacker.state.bonus_action_available is False

import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.recharge_action_policy import recharge_attack_choice
from app.combat.state import begin_turn
from app.domain.combatants import RechargeRule, ResourceDefinition
from app.domain.grid import GridPosition
from app.domain.models import EncounterSelection
from app.domain.runtime import ResourceState


def _resource_backed_bandit():
    try:
        setup = build_encounter_setup(EncounterSelection(
            hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-bandit"],
        ))
        attacker, target = setup.monsters[0], setup.heroes[0]
        attacker.state.position = GridPosition(x=8, y=6)
        target.state.position = GridPosition(x=7, y=6)
        attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        ranged = next(attack for attack in attacks if attack.weapon.attack_kind.value == "ranged")
        recharge_ranged = ranged.model_copy(update={"resource_id": "rock-recharge", "resource_cost": 1})
        alternates = [recharge_ranged if attack.id == ranged.id else attack for attack in attacker.state.template.alternate_weapon_attacks]
        primary = recharge_ranged if attacker.state.template.weapon_attack.id == ranged.id else attacker.state.template.weapon_attack
        definition = ResourceDefinition(
            id="rock-recharge", name="Rock Recharge", max_uses=1,
            recharge=RechargeRule(minimum_roll=6),
        )
        attacker.state.template = attacker.state.template.model_copy(update={
            "weapon_attack": primary,
            "alternate_weapon_attacks": alternates,
            "resources": [*attacker.state.template.resources, definition],
        })
        attacker.state.resources.append(ResourceState(
            id="rock-recharge", name="Rock Recharge", current_uses=1, max_uses=1,
        ))
        begin_turn(attacker.state)
        return setup, attacker, target, recharge_ranged
    except Exception as exc:
        raise RuntimeError("Recharge attack test setup failed.") from exc


def test_resource_backed_attack_spends_on_miss_and_logs_remaining() -> None:
    setup, attacker, target, attack = _resource_backed_bandit()

    event = resolve_attack(
        1, 1, attacker.state, target.state, attack, 5, FixedDiceProvider([2]),
        actor_event_id=attacker.combatant_id, target_event_id=target.combatant_id,
        affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
    )

    assert event.hit is False
    assert event.resource_remaining == 0
    assert attacker.state.resources[-1].current_uses == 0


def test_unavailable_resource_attack_fails_closed_before_roll() -> None:
    _setup, attacker, target, attack = _resource_backed_bandit()
    attacker.state.resources[-1].current_uses = 0

    with pytest.raises(RuntimeError, match="Attack resolution failed"):
        resolve_attack(1, 1, attacker.state, target.state, attack, 5, FixedDiceProvider([20]))

    assert attacker.state.resources[-1].current_uses == 0


def test_available_recharge_attack_is_prioritized_while_engaged() -> None:
    setup, attacker, _target, attack = _resource_backed_bandit()

    choice = recharge_attack_choice(attacker, setup)

    assert choice is not None
    assert choice[1].id == attack.id
    assert choice[2] == 5

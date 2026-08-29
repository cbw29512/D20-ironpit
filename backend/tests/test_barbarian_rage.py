from app.combat.attacks import resolve_attack
from app.combat.barbarian import (
    end_rage_if_incapacitated,
    enter_rage,
    finish_rage_turn,
    maintain_rage_with_bonus_action,
    rage_active,
)
from app.combat.damage import resolve_weapon_damage
from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.pregens import build_brom_ironmark
from app.domain.models import DamageType, ResourceDefinition, RollMode


def _barbarian_state():
    template = build_brom_ironmark().model_copy(deep=True)
    template.id = "test-barbarian-l1"
    template.name = "Test Barbarian"
    template.archetype = "Barbarian"
    template.rage_damage_bonus = 2
    template.wearing_heavy_armor = False
    template.weapon_attack.rage_eligible = True
    template.resources = [ResourceDefinition(id="rage", name="Rage", max_uses=2)]
    return build_combatant_state(template)


def test_enter_rage_spends_bonus_action_and_one_use() -> None:
    state = _barbarian_state()
    event = enter_rage(1, 1, state, "barbarian-1")

    assert event is not None
    assert event.event_type == "feature"
    assert event.resource_remaining == 1
    assert state.bonus_action_available is False
    assert rage_active(state)
    assert state.rage_expires_round == 2
    assert state.rage_max_round == 101
    assert set(state.temporary_damage_resistances) == {
        DamageType.BLUDGEONING,
        DamageType.PIERCING,
        DamageType.SLASHING,
    }


def test_rage_cannot_start_in_heavy_armor_or_restart_while_active() -> None:
    state = _barbarian_state()
    state.template.wearing_heavy_armor = True
    assert enter_rage(1, 1, state, "barbarian-1") is None
    assert state.resources[0].current_uses == 2

    state.template.wearing_heavy_armor = False
    assert enter_rage(1, 1, state, "barbarian-1") is not None
    begin_turn(state)
    assert enter_rage(2, 2, state, "barbarian-1") is None
    assert state.resources[0].current_uses == 1


def test_rage_adds_flat_damage_only_to_eligible_attacks() -> None:
    state = _barbarian_state()
    enter_rage(1, 1, state, "barbarian-1")

    normal, _ = resolve_weapon_damage(
        state, state.template.weapon_attack, FixedDiceProvider([6]), False, RollMode.NORMAL
    )
    critical, _ = resolve_weapon_damage(
        state, state.template.weapon_attack, FixedDiceProvider([6, 6]), True, RollMode.NORMAL
    )
    ineligible = state.template.weapon_attack.model_copy(deep=True)
    ineligible.rage_eligible = False
    no_rage_bonus, _ = resolve_weapon_damage(
        state, ineligible, FixedDiceProvider([6]), False, RollMode.NORMAL
    )

    assert normal.total == 11
    assert critical.total == 17
    assert no_rage_bonus.total == 9


def test_rage_resists_physical_damage_but_not_fire() -> None:
    state = _barbarian_state()
    enter_rage(1, 1, state, "barbarian-1")

    assert adjusted_damage_amount(7, DamageType.SLASHING, state) == 3
    assert adjusted_damage_amount(7, DamageType.FIRE, state) == 7


def test_attack_roll_extends_rage_even_when_attack_misses() -> None:
    attacker = _barbarian_state()
    defender = build_combatant_state(build_goblin_warrior())
    enter_rage(1, 1, attacker, "barbarian-1")
    begin_turn(attacker)

    event = resolve_attack(
        2,
        2,
        attacker,
        defender,
        attacker.template.weapon_attack,
        5,
        FixedDiceProvider([1]),
    )

    assert event.hit is False
    assert attacker.rage_expires_round == 3


def test_bonus_action_can_extend_rage_when_no_attack_was_made() -> None:
    state = _barbarian_state()
    enter_rage(1, 1, state, "barbarian-1")
    begin_turn(state)

    event = maintain_rage_with_bonus_action(2, 2, state, "barbarian-1")

    assert event is not None
    assert state.bonus_action_available is False
    assert state.rage_expires_round == 3


def test_rage_ends_when_not_extended_or_when_incapacitated() -> None:
    state = _barbarian_state()
    enter_rage(1, 1, state, "barbarian-1")
    finish_rage_turn(state, 2)
    assert rage_active(state) is False
    assert state.temporary_damage_resistances == []

    begin_turn(state)
    enter_rage(2, 3, state, "barbarian-1")
    state.is_unconscious = True
    end_rage_if_incapacitated(state)
    assert rage_active(state) is False
    assert state.rage_max_round is None


def test_rage_cannot_extend_past_ten_minute_limit() -> None:
    state = _barbarian_state()
    enter_rage(1, 1, state, "barbarian-1")
    state.rage_expires_round = 101
    begin_turn(state)

    assert maintain_rage_with_bonus_action(2, 101, state, "barbarian-1") is None
    finish_rage_turn(state, 101)
    assert rage_active(state) is False

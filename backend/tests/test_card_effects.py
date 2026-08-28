from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.dodge import take_dodge_action
from app.combat.lifecycle import begin_actor_turn
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior


def test_sap_is_applied_to_target_card_and_removed_when_consumed() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())

    applied = resolve_attack(
        1, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([15, 4]),
    )
    assert any(
        change.operation == "apply"
        and change.kind == "debuff"
        and change.actor_id == goblin.template.id
        and change.label == "Sap"
        for change in applied.effect_changes
    )

    consumed = resolve_attack(
        2, 1, goblin, fighter, goblin.template.weapon_attack, 5,
        FixedDiceProvider([15, 10]),
    )
    assert any(
        change.operation == "remove"
        and change.actor_id == goblin.template.id
        and change.effect_id.startswith("sap:")
        for change in consumed.effect_changes
    )


def test_vex_is_a_buff_on_attacker_card_and_removes_on_matching_attack() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    handaxe = fighter.template.alternate_weapon_attacks[0]

    applied = resolve_attack(
        1, 1, fighter, goblin, handaxe, 20, FixedDiceProvider([15, 4])
    )
    assert any(
        change.operation == "apply"
        and change.kind == "buff"
        and change.actor_id == fighter.template.id
        and change.label == "Vex"
        for change in applied.effect_changes
    )

    consumed = resolve_attack(
        2, 1, fighter, goblin, handaxe, 20, FixedDiceProvider([1, 2])
    )
    vex_changes = [
        change for change in consumed.effect_changes if change.effect_id.startswith("vex:")
    ]
    assert len(vex_changes) == 1
    assert vex_changes[0].operation == "remove"


def test_dodge_card_buff_expires_at_start_of_next_turn() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())

    dodge = take_dodge_action(1, 1, fighter)
    assert dodge.effect_changes[0].operation == "apply"
    assert dodge.effect_changes[0].label == "Dodge"

    events, _ = begin_actor_turn(2, 2, fighter, (fighter, goblin))
    assert len(events) == 1
    assert events[0].log_visible is False
    assert events[0].effect_changes[0].operation == "remove"
    assert events[0].effect_changes[0].effect_id == "dodge"


def test_unused_sap_card_debuff_expires_at_source_turn_start() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    resolve_attack(
        1, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([15, 4]),
    )

    events, _ = begin_actor_turn(2, 2, fighter, (fighter, goblin))

    assert any(
        change.operation == "remove"
        and change.actor_id == goblin.template.id
        and change.effect_id.startswith("sap:")
        for event in events
        for change in event.effect_changes
    )

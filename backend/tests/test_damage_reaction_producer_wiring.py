from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.save_targets import resolve_save_targets
from app.combat.standard_attack_action import resolve_standard_attack_action
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.reactions import DamageReactionAttack


def _member(combatant_id: str, side: str, position: int, template) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _reaction_target() -> EncounterCombatant:
    template = build_demo_fighter()
    template.damage_reaction_attack = DamageReactionAttack(source_feature="retaliation")
    return _member("target", "monsters", 5, template)


def _attacker() -> EncounterCombatant:
    return _member("attacker", "heroes", 0, build_demo_fighter())


def test_standard_attack_action_emits_immediate_damage_reaction() -> None:
    attacker = _attacker()
    target = _reaction_target()
    setup = EncounterSetup(
        heroes=[attacker],
        monsters=[target],
        hero_total_levels=1,
        monster_total_cr="1",
    )

    events, sequence = resolve_standard_attack_action(
        1,
        1,
        attacker,
        target,
        attacker.state.template.weapon_attack,
        5,
        FixedDiceProvider([19, 5, 19, 5]),
        setup,
        "1:attacker",
        allow_reckless=False,
    )

    assert len(events) >= 2
    assert events[0].actor_id == attacker.combatant_id
    assert events[1].feature_id == "retaliation"
    assert events[1].actor_id == target.combatant_id
    assert events[1].target_id == attacker.combatant_id
    assert target.state.reaction_available is False
    assert sequence >= 3


def test_save_damage_emits_immediate_damage_reaction() -> None:
    attacker = _attacker()
    target = _reaction_target()
    setup = EncounterSetup(
        heroes=[attacker],
        monsters=[target],
        hero_total_levels=1,
        monster_total_cr="1",
    )
    action = SavingThrowAction(
        id="test-blast",
        name="Test Blast",
        save_ability="dexterity",
        dc=20,
        range_ft=30,
        damage_dice_count=1,
        damage_dice_size=6,
        damage_type="force",
        success_damage="none",
    )

    events, sequence = resolve_save_targets(
        1,
        1,
        attacker,
        setup,
        action,
        (target.combatant_id,),
        FixedDiceProvider([1, 6, 19, 5]),
    )

    assert len(events) == 2
    assert events[0].event_type == "saving_throw"
    assert events[0].feature_id == "test-blast"
    assert events[1].feature_id == "retaliation"
    assert events[1].actor_id == target.combatant_id
    assert events[1].target_id == attacker.combatant_id
    assert target.state.reaction_available is False
    assert sequence == 3

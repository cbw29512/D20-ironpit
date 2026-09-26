from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.reaction_roll_penalties import apply_reaction_roll_penalty_if_useful
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import DiceRoll
from app.domain.reaction_roll_penalties import ReactionRollPenaltyAction


def _action() -> ReactionRollPenaltyAction:
    return ReactionRollPenaltyAction(
        id="test-penalty",
        name="Test Penalty",
        range_ft=60,
        resource_id="penalty-use",
        dice_size=8,
        roll_kinds=["attack", "ability_check", "damage"],
        requires_source_sight=True,
        requires_target_hearing=True,
        blocked_target_condition_immunity="charmed",
        priority=20,
    )


def _member(combatant_id: str, side: str, position: int, *, reactor: bool = False):
    update = {"id": f"{combatant_id}-template", "name": combatant_id.title(), "ruleset": "2014"}
    if reactor:
        update["resources"] = [ResourceDefinition(id="penalty-use", name="Penalty Use", max_uses=2)]
        update["reaction_roll_penalty_actions"] = [_action()]
    template = build_commoner().model_copy(update=update)
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup():
    roller = _member("roller", "monsters", 20)
    reactor = _member("reactor", "heroes", 0, reactor=True)
    ally = _member("ally", "heroes", 5)
    return EncounterSetup(
        heroes=[reactor, ally],
        monsters=[roller],
        hero_total_levels=2,
        monster_total_cr="0",
        ruleset="2014",
    ), roller, reactor


def _roll(total: int, natural: int = 12) -> DiceRoll:
    return DiceRoll(
        notation="1d20+4", rolls=[natural], selected_roll=natural, modifier=4, total=total,
    )


def test_reaction_penalty_spends_reaction_and_resource_when_it_can_flip_attack() -> None:
    setup, roller, reactor = _setup()
    result = apply_reaction_roll_penalty_if_useful(
        roller, setup, "attack", _roll(16), FixedDiceProvider([3]), threshold=15,
    )
    assert result is not None
    assert result.roll.total == 13
    assert result.roll.revisions[-1].kind == "roll_penalty"
    assert result.penalty_total == 3
    assert reactor.state.reaction_available is False
    assert reactor.state.resources[0].current_uses == 1


def test_reaction_penalty_preserves_resource_when_attack_cannot_change() -> None:
    setup, roller, reactor = _setup()
    assert apply_reaction_roll_penalty_if_useful(
        roller, setup, "attack", _roll(25), FixedDiceProvider([8]), threshold=15,
    ) is None
    assert reactor.state.reaction_available is True
    assert reactor.state.resources[0].current_uses == 2


def test_reaction_penalty_does_not_attempt_to_change_natural_twenty() -> None:
    setup, roller, reactor = _setup()
    assert apply_reaction_roll_penalty_if_useful(
        roller, setup, "attack", _roll(24, natural=20), FixedDiceProvider([8]), threshold=15,
    ) is None
    assert reactor.state.reaction_available is True


def test_reaction_penalty_obeys_sight_hearing_and_charm_immunity() -> None:
    for blocker in ("blinded-source", "deafened-target", "charm-immune"):
        setup, roller, reactor = _setup()
        if blocker == "blinded-source":
            reactor.state.active_effect_ids.append("blinded")
        elif blocker == "deafened-target":
            roller.state.active_effect_ids.append("deafened")
        else:
            roller.state.template.condition_immunities = ["charmed"]
        assert apply_reaction_roll_penalty_if_useful(
            roller, setup, "attack", _roll(16), FixedDiceProvider([8]), threshold=15,
        ) is None
        assert reactor.state.reaction_available is True


def test_damage_penalty_reduces_damage_but_not_below_zero() -> None:
    setup, roller, reactor = _setup()
    damage = DiceRoll(notation="1d6+2", rolls=[2], modifier=2, total=4)
    result = apply_reaction_roll_penalty_if_useful(
        roller, setup, "damage", damage, FixedDiceProvider([7]),
    )
    assert result is not None
    assert result.roll.total == 0
    assert reactor.state.reaction_available is False


def test_weapon_attack_integration_uses_reaction_penalty_before_hit_resolution() -> None:
    setup, roller, reactor = _setup()
    target = setup.heroes[1]
    target.state.template.armor_class = 13
    event = resolve_encounter_attack(
        1,
        1,
        roller,
        target,
        roller.state.template.weapon_attack,
        5,
        FixedDiceProvider([12, 3]),
        setup,
        spend_action=False,
    )
    assert event.attack_roll is not None
    assert event.attack_roll.revisions[-1].kind == "roll_penalty"
    assert event.attack_roll.total < event.target_ac
    assert event.hit is False
    assert reactor.state.reaction_available is False
    assert reactor.state.resources[0].current_uses == 1

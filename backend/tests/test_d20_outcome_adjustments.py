from __future__ import annotations

from app.combat.d20_outcome_adjustments import (
    apply_resource_backed_d20_outcome_adjustment_if_useful,
)
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.event_support import DiceRoll
from app.domain.progression_primitives import ResourceBackedD20OutcomeAdjustment


def _member(
    combatant_id: str,
    side: str,
    position: int,
    *,
    fate: bool = False,
) -> EncounterCombatant:
    template = build_commoner().model_copy(deep=True)
    template.id = f"{combatant_id}-template"
    template.name = combatant_id.title()
    if fate:
        template.resources = [
            ResourceDefinition(id="fate-use", name="Fate Use", max_uses=1),
        ]
        template.progression_features.resource_backed_d20_outcome_adjustments = [
            ResourceBackedD20OutcomeAdjustment(
                source_id="test-fate",
                source_name="Test Fate",
                resource_id="fate-use",
                dice_count=2,
                dice_size=4,
                range_ft=60,
                test_kinds=["attack", "saving_throw", "ability_check"],
                can_add=True,
                can_subtract=True,
            ),
        ]
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _roll(total: int, natural: int = 10) -> DiceRoll:
    return DiceRoll(
        notation="1d20+2",
        rolls=[natural],
        selected_roll=natural,
        modifier=2,
        total=total,
    )


def test_adjustment_adds_to_allied_failed_test_when_it_can_flip_outcome() -> None:
    source = _member("source", "heroes", 0, fate=True)
    roller = _member("roller", "heroes", 20)
    enemy = _member("enemy", "monsters", 20)
    setup = EncounterSetup(
        heroes=[source, roller],
        monsters=[enemy],
        hero_total_levels=2,
        monster_total_cr="0",
        ruleset="2024",
    )

    result = apply_resource_backed_d20_outcome_adjustment_if_useful(
        roller,
        setup,
        "saving_throw",
        _roll(12),
        15,
        FixedDiceProvider([2, 2]),
    )

    assert result is not None
    assert result.direction == "add"
    assert result.adjustment_total == 4
    assert result.roll.total == 16
    assert result.roll.revisions[-1].kind == "roll_adjustment"
    assert source.state.resources[0].current_uses == 0


def test_adjustment_subtracts_from_hostile_success_when_it_can_flip_outcome() -> None:
    source = _member("source", "heroes", 0, fate=True)
    roller = _member("roller", "monsters", 20)
    setup = EncounterSetup(
        heroes=[source],
        monsters=[roller],
        hero_total_levels=1,
        monster_total_cr="0",
        ruleset="2024",
    )

    result = apply_resource_backed_d20_outcome_adjustment_if_useful(
        roller,
        setup,
        "ability_check",
        _roll(16),
        15,
        FixedDiceProvider([2, 1]),
    )

    assert result is not None
    assert result.direction == "subtract"
    assert result.roll.total == 13
    assert source.state.resources[0].current_uses == 0


def test_adjustment_preserves_resource_when_out_of_range_or_unable_to_flip() -> None:
    source = _member("source", "heroes", 0, fate=True)
    roller = _member("roller", "heroes", 80)
    setup = EncounterSetup(
        heroes=[source, roller],
        monsters=[],
        hero_total_levels=2,
        monster_total_cr="0",
        ruleset="2024",
    )

    assert apply_resource_backed_d20_outcome_adjustment_if_useful(
        roller,
        setup,
        "saving_throw",
        _roll(12),
        15,
        FixedDiceProvider([4, 4]),
    ) is None
    assert source.state.resources[0].current_uses == 1

    roller.position_ft = 20
    assert apply_resource_backed_d20_outcome_adjustment_if_useful(
        roller,
        setup,
        "saving_throw",
        _roll(2),
        15,
        FixedDiceProvider([4, 4]),
    ) is None
    assert source.state.resources[0].current_uses == 1


def test_attack_natural_one_or_twenty_is_not_adjusted() -> None:
    source = _member("source", "heroes", 0, fate=True)
    roller = _member("roller", "monsters", 20)
    setup = EncounterSetup(
        heroes=[source],
        monsters=[roller],
        hero_total_levels=1,
        monster_total_cr="0",
        ruleset="2024",
    )

    assert apply_resource_backed_d20_outcome_adjustment_if_useful(
        roller,
        setup,
        "attack",
        _roll(22, natural=20),
        15,
        FixedDiceProvider([4, 4]),
        natural_attack_roll=20,
    ) is None
    assert source.state.resources[0].current_uses == 1

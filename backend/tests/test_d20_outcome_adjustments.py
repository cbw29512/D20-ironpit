from app.combat.d20_outcome_adjustments import adjust_d20_outcome
from app.combat.dice import FixedDiceProvider
from app.combat.rolls import roll_d20
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.event_support import RollMode
from app.domain.progression_riders import D20OutcomeAdjustmentRule


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template.model_copy(deep=True)),
    )


def _grant_fate(member: EncounterCombatant) -> None:
    member.state.template.progression_features.d20_outcome_adjustment = D20OutcomeAdjustmentRule(
        source_id="boon-of-fate",
        resource_id="boon-of-fate",
        range_ft=60,
        dice_count=2,
        dice_size=4,
    )
    member.state.template.resources.append(
        ResourceDefinition(id="boon-of-fate", name="Boon of Fate", max_uses=1)
    )
    member.state.resources.append(
        type(member.state.resources[0])(
            id="boon-of-fate", name="Boon of Fate", current_uses=1, max_uses=1,
        )
    )


def test_fate_helps_failed_ally_and_records_adjustment_dice() -> None:
    roller = _member(build_karnok_stoneward(), "roller", "heroes", 0)
    source = _member(build_karnok_stoneward(), "source", "heroes", 10)
    enemy = _member(build_goblin_warrior(), "enemy", "monsters", 20)
    _grant_fate(source)
    setup = EncounterSetup(heroes=[roller, source], monsters=[enemy], hero_total_levels=2, monster_total_cr="1/4")
    roll = roll_d20(FixedDiceProvider([8]), 0, RollMode.NORMAL)

    updated, succeeded, source_id = adjust_d20_outcome(
        roll, False, 12, roller, setup, FixedDiceProvider([2, 3]),
    )

    assert succeeded is True and source_id == "source"
    assert updated.total == 13
    revision = updated.revisions[-1]
    assert revision.kind == "total_adjustment"
    assert revision.adjustment_rolls == [2, 3] and revision.adjustment_sign == 1
    assert next(item for item in source.state.resources if item.id == "boon-of-fate").current_uses == 0


def test_fate_penalizes_enemy_success_but_skips_impossible_or_locked_outcomes() -> None:
    source = _member(build_karnok_stoneward(), "source", "heroes", 0)
    enemy = _member(build_goblin_warrior(), "enemy", "monsters", 10)
    _grant_fate(source)
    setup = EncounterSetup(heroes=[source], monsters=[enemy], hero_total_levels=1, monster_total_cr="1/4")

    roll = roll_d20(FixedDiceProvider([15]), 0, RollMode.NORMAL)
    updated, succeeded, source_id = adjust_d20_outcome(
        roll, True, 12, enemy, setup, FixedDiceProvider([2, 3]),
    )
    assert succeeded is False and source_id == "source" and updated.total == 10
    assert updated.revisions[-1].adjustment_sign == -1

    source.state.resources[-1].current_uses = 1
    far_enemy = enemy.model_copy(deep=True)
    far_enemy.position_ft = 100
    unchanged, _, source_id = adjust_d20_outcome(
        roll, True, 12, far_enemy, setup, FixedDiceProvider([4, 4]),
    )
    assert unchanged == roll and source_id is None

    locked, _, source_id = adjust_d20_outcome(
        roll, True, 12, enemy, setup, FixedDiceProvider([4, 4]), outcome_locked=True,
    )
    assert locked == roll and source_id is None

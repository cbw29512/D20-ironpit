import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.healing import choose_healing_target, resolve_healing
from app.domain.models import EncounterSelection, HealingAction


@pytest.mark.parametrize("creature_type", ["Undead", "Construct", "Undead (shapechanger)"])
def test_healing_action_rejects_source_owned_excluded_creature_types(creature_type: str) -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        monster_ids=["srd-goblin-warrior"],
    ))
    healer, target = setup.heroes
    target.state.template.creature_type = creature_type
    target.state.current_hp = 1
    action = HealingAction(
        id="typed-heal",
        name="Typed Heal",
        action_cost="action",
        range_ft=60,
        target_mode="self_or_ally",
        dice_count=1,
        dice_size=8,
        healing_bonus=3,
        excluded_creature_types=["undead", "construct"],
    )

    assert choose_healing_target(healer, setup, action) is None
    with pytest.raises(ValueError):
        resolve_healing(
            1,
            1,
            healer,
            target,
            action,
            FixedDiceProvider([8]),
        )


def test_healing_action_allows_nonexcluded_creature_type() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        monster_ids=["srd-goblin-warrior"],
    ))
    healer, target = setup.heroes
    target.state.template.creature_type = "Humanoid"
    target.state.current_hp = 1
    action = HealingAction(
        id="typed-heal",
        name="Typed Heal",
        action_cost="action",
        range_ft=60,
        target_mode="self_or_ally",
        dice_count=1,
        dice_size=8,
        healing_bonus=3,
        excluded_creature_types=["undead", "construct"],
    )

    assert choose_healing_target(healer, setup, action) is target

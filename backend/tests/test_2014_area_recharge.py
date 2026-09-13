from app.combat.area_save_actions import resolve_area_save_action
from app.combat.area_targeting import legal_area_placements
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.combatants import RechargeRule, ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.models import SavingThrowAction
from app.domain.targeting import AreaTargeting


def _member(combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(deep=True)
    template.saving_throw_bonuses = {"dexterity": 2}
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=x * 5,
        state=state,
    )


def test_recharge_line_spends_one_resource_and_uses_one_shared_damage_roll() -> None:
    actor = _member("monster-1:breather", "monsters", 1, 1)
    first = _member("hero-1:first", "heroes", 2, 1)
    second = _member("hero-2:second", "heroes", 3, 1)
    actor.state.template.resources = [
        ResourceDefinition(
            id="fire-breath", name="Fire Breath", max_uses=1,
            recharge=RechargeRule(minimum_roll=5),
        )
    ]
    actor.state.resources = build_combatant_state(actor.state.template).resources
    action = SavingThrowAction(
        id="fire-breath", name="Fire Breath", save_ability="dexterity", dc=20,
        range_ft=30,
        area=AreaTargeting(shape="line", origin="self", length_ft=30, width_ft=5),
        damage_dice_count=2, damage_dice_size=6, damage_type="fire",
        success_damage="half", resource_id="fire-breath",
    )
    setup = EncounterSetup(
        heroes=[first, second], monsters=[actor], hero_total_levels=2,
        monster_total_cr="1/4",
        map_definition=BattleMapDefinition(id="test", width_squares=10, height_squares=10),
    )
    placement = legal_area_placements(actor, setup, action.area, action.range_ft)[0]
    events, sequence, _ = resolve_area_save_action(
        1, 1, actor, setup, action, FixedDiceProvider([3, 4, 1, 1]), placement=placement,
    )
    assert sequence == 3
    assert len(events) == 2
    assert actor.state.resources[0].current_uses == 0
    assert events[0].damage_components[0].rolls == [3, 4]
    assert events[1].damage_components[0].rolls == [3, 4]
    assert events[0].resource_remaining == 0
    assert events[1].resource_remaining == 0

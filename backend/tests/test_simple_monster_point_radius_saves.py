from app.combat.dice import FixedDiceProvider
from app.combat.save_area_targeting import area_targets
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.monster_catalog import load_monster_rows
from app.content.simple_monster_source_definitions import audited_source_definition
from app.domain.actions import SaveConditionEffect, SavingThrowAction
from app.domain.areas import AreaGeometry
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.size import CreatureSize


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _member(combatant_id: str, side: str, position_ft: int, size: CreatureSize) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(update={"size": size})
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position_ft,
        state=build_combatant_state(template),
    )


def test_giant_ape_point_radius_save_is_source_derived_and_audited() -> None:
    definition = audited_source_definition(_row("Giant Ape"))
    assert definition is not None
    action = next(item for item in definition.save_actions if item.name.startswith("Boulder Toss"))
    assert action.range_ft == 90
    assert action.area == AreaGeometry(shape="radius", size_ft=5)
    assert action.damage is not None
    assert (action.damage.count, action.damage.size, action.damage.bonus) == (7, 6, 0)
    assert action.damage_type.value == "bludgeoning"
    assert action.success_damage == "half"
    assert len(action.failure_conditions) == 1
    prone = action.failure_conditions[0]
    assert prone.condition == "prone"
    assert prone.max_target_size == CreatureSize.LARGE
    assert action.resource_id is not None


def test_failed_save_condition_honors_its_own_size_limit() -> None:
    actor = _member("monster:actor", "monsters", 0, CreatureSize.MEDIUM)
    large = _member("hero:large", "heroes", 5, CreatureSize.LARGE)
    huge = _member("hero:huge", "heroes", 5, CreatureSize.HUGE)
    action = SavingThrowAction(
        id="size-gated-prone", name="Size Gated Prone", save_ability="strength", dc=40, range_ft=10,
        failure_conditions=[SaveConditionEffect(condition_id="prone", max_target_size=CreatureSize.LARGE)],
    )
    resolve_save_action(1, 1, actor, large, action, 5, FixedDiceProvider([1]), spend_action=False)
    resolve_save_action(2, 1, actor, huge, action, 5, FixedDiceProvider([1]), spend_action=False)
    assert "prone" in large.state.active_effect_ids
    assert "prone" not in huge.state.active_effect_ids


def test_point_radius_can_reach_past_point_range_by_its_radius() -> None:
    actor = _member("monster:actor", "monsters", 0, CreatureSize.MEDIUM)
    target = _member("hero:target", "heroes", 95, CreatureSize.MEDIUM)
    setup = EncounterSetup(
        heroes=[target], monsters=[actor], hero_total_levels=1,
        monster_total_cr="1/4", starting_distance_ft=95,
    )
    action = SavingThrowAction(
        id="point-radius", name="Point Radius", save_ability="dexterity", dc=10, range_ft=90,
        area=AreaGeometry(shape="radius", size_ft=5),
    )
    assert area_targets(actor, setup, action) == [target]

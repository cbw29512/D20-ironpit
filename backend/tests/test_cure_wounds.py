from app.combat.dice import FixedDiceProvider
from app.combat.healing import choose_healing_action, resolve_healing
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.audited_fighter import build_karnok_stoneward
from app.content.healing_spell_effects import build_cure_wounds
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(combatant_id: str, position_ft: int, *, healer: bool = False):
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"
    template.name = combatant_id
    if healer:
        template.healing_actions = [build_cure_wounds(3)]
        template.resources = [ResourceDefinition(id="spell-slot-1", name="Level 1 Slot", max_uses=2)]
    return EncounterCombatant(
        combatant_id=combatant_id,
        side="heroes",
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def _enemy(position_ft: int = 10):
    return EncounterCombatant(
        combatant_id="enemy",
        side="monsters",
        position_ft=position_ft,
        state=build_combatant_state(build_karnok_stoneward()),
    )


def test_cure_wounds_rescues_adjacent_zero_hp_ally_with_printed_level_slot() -> None:
    healer = _member("healer", 0, healer=True)
    ally = _member("ally", 5)
    setup = EncounterSetup(
        heroes=[healer, ally], monsters=[_enemy()], hero_total_levels=2, monster_total_cr="1",
    )
    relentless = next(item for item in ally.state.resources if item.id == "relentless-endurance")
    relentless.current_uses = 0
    apply_damage(ally.state, ally.state.current_hp)
    ally.state.death_save_failures = 2

    choice = choose_healing_action(healer, setup)
    assert choice is not None
    action, target = choice
    assert action.id == "cure-wounds"
    assert action.action_cost == "action"
    assert action.range_ft == 5
    assert action.dice_count == 2 and action.dice_size == 8 and action.healing_bonus == 3
    assert target is ally

    event = resolve_healing(1, 1, healer, ally, action, FixedDiceProvider([8, 7]))
    assert event.healing_roll is not None
    assert event.healing_roll.total == 18
    assert event.hp_before == 0
    assert event.hp_after == min(18, ally.state.template.max_hp)
    assert ally.state.is_unconscious is False
    assert ally.state.death_save_successes == 0
    assert ally.state.death_save_failures == 0
    assert healer.state.action_available is False
    assert next(item for item in healer.state.resources if item.id == "spell-slot-1").current_uses == 1


def test_cure_wounds_cannot_reach_beyond_touch_formation_band() -> None:
    healer = _member("healer", 0, healer=True)
    ally = _member("ally", 10)
    ally.state.current_hp = 1
    setup = EncounterSetup(
        heroes=[healer, ally], monsters=[_enemy()], hero_total_levels=2, monster_total_cr="1",
    )
    assert choose_healing_action(healer, setup) is None


def test_cure_wounds_does_not_substitute_a_higher_level_slot_while_upcasting_is_deferred() -> None:
    healer = _member("healer", 0, healer=True)
    healer.state.resources = [
        item.model_copy(update={"id": "spell-slot-2", "name": "Level 2 Slot", "current_uses": 1, "max_uses": 1})
        for item in healer.state.resources[:1]
    ]
    ally = _member("ally", 5)
    ally.state.current_hp = 1
    setup = EncounterSetup(
        heroes=[healer, ally], monsters=[_enemy()], hero_total_levels=2, monster_total_cr="1",
    )
    assert choose_healing_action(healer, setup) is None
    assert healer.state.resources[0].current_uses == 1

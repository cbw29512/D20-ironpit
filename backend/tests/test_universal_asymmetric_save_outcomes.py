"""Source-neutral saved-result composition; failed zero HP is never damage."""
from __future__ import annotations

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import _compile_save
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.content.capability_compiler import compile_combatant
from app.domain.actions import SavingThrowAction
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.combatants import DamageType
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _monster(cid: str) -> EncounterCombatant:
    printed = next(row for row in load_monster_source_2014() if row.id == "commoner")
    template = compile_combatant(adapt_basic_monster_2014(printed)).model_copy(update={"max_hp": 60})
    return EncounterCombatant(combatant_id=cid, side="monsters", position_ft=5,
                              state=build_combatant_state(template))


def _hero() -> EncounterCombatant:
    template = build_aurelia_brightshield_2014(1).model_copy(update={"max_hp": 60})
    return EncounterCombatant(combatant_id="hero", side="heroes", position_ft=10,
                              state=build_combatant_state(template))


def _action(dc: int) -> SavingThrowAction:
    return SavingThrowAction(
        id="renamed-cry", name="Renamed Source-Independent Cry",
        save_ability="constitution", dc=dc, range_ft=30,
        damage_dice_count=3, damage_dice_size=6, damage_type="psychic",
        failure_sets_zero_hp=True, damage_only_on_success=True,
    )


def test_failed_save_sets_friendly_monster_to_zero_without_consuming_temp_hp() -> None:
    actor, ally, hero = _monster("source"), _monster("friend"), _hero()
    ally.state.temporary_hp = 9
    setup = EncounterSetup(heroes=[hero], monsters=[actor, ally],
                           hero_total_levels=1, monster_total_cr="0", ruleset="2014")
    event = resolve_save_action(1, 1, actor, ally, _action(30), 5, FixedDiceProvider([1]),
                                spend_action=False, affected_states=[x.state for x in [actor, ally, hero]],
                                setup=setup)
    assert event.save_succeeded is False
    assert event.damage_roll is None and event.damage_components == []
    assert ally.state.current_hp == 0 and ally.state.is_dead
    assert ally.state.temporary_hp == 9
    assert "directly to 0 HP" in event.description


def test_failed_save_sets_pregen_to_dying_without_damage_failures() -> None:
    actor, hero = _monster("source"), _hero()
    hero.state.temporary_hp = 8
    setup = EncounterSetup(heroes=[hero], monsters=[actor],
                           hero_total_levels=1, monster_total_cr="0", ruleset="2014")
    event = resolve_save_action(1, 1, actor, hero, _action(30), 5, FixedDiceProvider([1]),
                                spend_action=False, affected_states=[actor.state, hero.state], setup=setup)
    assert not event.save_succeeded
    assert hero.state.current_hp == 0 and hero.state.is_unconscious and not hero.state.is_dead
    assert hero.state.death_save_failures == 0 and hero.state.temporary_hp == 8


def test_success_delivers_printed_full_typed_damage_not_zero_hp() -> None:
    actor, hero = _monster("source"), _hero()
    setup = EncounterSetup(heroes=[hero], monsters=[actor],
                           hero_total_levels=1, monster_total_cr="0", ruleset="2014")
    event = resolve_save_action(1, 1, actor, hero, _action(1), 5,
                                FixedDiceProvider([20, 1, 2, 3]),
                                spend_action=False, affected_states=[actor.state, hero.state], setup=setup)
    assert event.save_succeeded is True
    assert event.damage_roll is not None and event.damage_roll.total == 6
    assert hero.state.current_hp == 54 and not hero.state.is_dead
    assert [part.damage_type for part in event.damage_components] == [DamageType.PSYCHIC]


def test_source_schema_compiles_and_rejects_conflicting_outcomes() -> None:
    definition = SaveCapabilityDefinition(
        id="any-card", name="Arbitrary Ability", save_ability="constitution", dc=13,
        range_ft=30, damage=DiceSpec(count=3, size=6),
        damage_type=DamageType.PSYCHIC, damage_only_on_success=True,
        failure_sets_zero_hp=True,
    )
    runtime = _compile_save(definition)
    assert runtime.failure_sets_zero_hp and runtime.damage_only_on_success
    assert "failure_sets_zero_hp" in definition.model_dump()
    with pytest.raises(ValueError):
        SaveCapabilityDefinition.model_validate({**definition.model_dump(), "damage_only_on_success": False})
    with pytest.raises(ValueError):
        SavingThrowAction.model_validate({**runtime.model_dump(), "success_damage": "half"})

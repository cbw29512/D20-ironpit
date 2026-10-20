"""Synthetic source-neutral target-selected saving throw regressions."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.combat.state import build_combatant_state
from app.combat.saving_throws import resolve_save_action
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.combat.dice import FixedDiceProvider
from app.domain.save_damage import SaveDamageComponent
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.combat.target_chosen_save import choose_save_ability
from app.content.demo import build_demo_fighter
from app.domain.character_builds import AbilityScores
from app.content.capability_compiler import _compile_save
from app.domain.capability_attacks import SaveCapabilityDefinition


def _target():
    # A manufactured template tests the engine rather than a named monster.
    template = build_demo_fighter()
    bonuses = dict(template.saving_throw_bonuses)
    bonuses.update(strength=2, dexterity=4)
    template = template.model_copy(update={
        "saving_throw_bonuses": bonuses,
        "ability_scores": AbilityScores(
            strength=12, dexterity=14, constitution=12,
            intelligence=10, wisdom=10, charisma=10,
        ),
    })
    return build_combatant_state(template)


def test_chooses_best_live_save_before_rolling() -> None:
    target = _target()
    options = ["strength", "dexterity"]
    assert choose_save_ability(target, options, 16) == "dexterity"

    # A higher Dexterity bonus loses to an unrestricted Strength roll if
    # Restrained imposes Disadvantage on the Dexterity save.
    target.active_effect_ids.append("restrained")
    assert choose_save_ability(target, options, 16) == "strength"
    target.active_effect_ids.remove("restrained")

    # All score changes are fight-state only; the source card stays immutable.
    original = target.template.ability_scores.score("dexterity")
    target.ability_score_reductions["dexterity"] = 10
    assert choose_save_ability(target, options, 16) == "strength"
    assert target.template.ability_scores.score("dexterity") == original


def test_save_choices_compile_and_fail_closed_on_bad_cards() -> None:
    definition = SaveCapabilityDefinition(
        id="renamed-source", name="Custom Landing Shock",
        save_ability="strength", save_ability_choices=["strength", "dexterity"],
        dc=16, range_ft=15,
    )
    compiled = _compile_save(definition)
    assert compiled.save_ability_choices == ["strength", "dexterity"]
    assert compiled.name == "Custom Landing Shock"
    with pytest.raises(ValidationError, match="distinct"):
        SaveCapabilityDefinition(
            id="wrong", name="Unknown Source", save_ability="strength",
            save_ability_choices=["strength", "strength"], dc=16, range_ft=15,
        )
    with pytest.raises(ValueError, match="distinct"):
        choose_save_ability(_target(), ["strength", "strength"], 16)


def test_generic_composed_save_applies_two_damage_types_and_prone_on_failure() -> None:
    # A renamed synthetic action proves the consumer is the universal save
    # resolver, not creature-specific Deadly Leap branching.
    definition = SaveCapabilityDefinition(
        id="custom-impact", name="Custom Landing Shock",
        save_ability="strength",
        save_ability_choices=["strength", "dexterity"], dc=16, range_ft=15,
        success_damage="half",
        damage_components=[
            SaveDamageComponent(dice_count=3, dice_size=6, damage_bonus=4, damage_type="bludgeoning"),
            SaveDamageComponent(dice_count=3, dice_size=6, damage_bonus=4, damage_type="slashing"),
        ],
        failed_save_timed_effect=FailedSaveTimedEffect(effect_id="prone"),
    )
    action = _compile_save(definition)
    source_state = _target()
    target_state = _target()
    target_state.current_hp = 100
    source = EncounterCombatant(combatant_id="source", side="monsters", position_ft=0, state=source_state)
    target = EncounterCombatant(combatant_id="target", side="heroes", position_ft=5, state=target_state)
    setup = EncounterSetup(
        heroes=[target], monsters=[source], ruleset="2014",
        hero_total_levels=1, monster_total_cr="1",
    )
    event = resolve_save_action(1, 1, source, target, action, 5, FixedDiceProvider([1] * 7), setup=setup)
    assert event.save_ability == "dexterity"
    assert event.save_succeeded is False
    assert [part.damage_type.value for part in event.damage_components] == ["bludgeoning", "slashing"]
    assert "prone" in target.state.active_effect_ids
    assert action.save_ability == "strength"
    assert action.save_ability_choices == ["strength", "dexterity"]



def test_grouped_failed_save_conditions_share_one_lifecycle() -> None:
    definition = SaveCapabilityDefinition(
        id="renamed-group-control",
        name="Renamed Group Control",
        save_ability="wisdom",
        dc=16,
        range_ft=30,
        failed_save_timed_effect=FailedSaveTimedEffect(
            effect_id="charmed",
            additional_effect_ids=["incapacitated"],
            repeat_save_ability="wisdom",
            repeat_save_dc=16,
            repeat_save_timing="target_turn_end",
            source_effect_immunity_on_end=True,
        ),
    )
    action = _compile_save(definition)
    source_state = _target()
    target_state = _target()
    source = EncounterCombatant(
        combatant_id="source", side="monsters", position_ft=0, state=source_state,
    )
    target = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=5, state=target_state,
    )
    setup = EncounterSetup(
        heroes=[target], monsters=[source], ruleset="2014",
        hero_total_levels=1, monster_total_cr="1",
    )

    event = resolve_save_action(
        1, 1, source, target, action, 5, FixedDiceProvider([1]), setup=setup,
    )

    assert event.applied_condition_ids == ["charmed", "incapacitated"]
    assert {"charmed", "incapacitated"} <= set(target.state.active_effect_ids)
    primary = next(effect for effect in target.state.timed_effects if effect.effect_id == "charmed")
    secondary = next(
        effect for effect in target.state.timed_effects if effect.effect_id == "incapacitated"
    )
    assert primary.repeat_save_timing == "target_turn_end"
    assert secondary.repeat_save_timing is None
    assert primary.source_effect_id == secondary.source_effect_id == action.id
    assert remove_effect_group(target.state, primary) == ["charmed", "incapacitated"]
    assert action.failed_save_timed_effect.additional_effect_ids == ["incapacitated"]


def test_grouped_failed_save_condition_ids_must_be_distinct() -> None:
    with pytest.raises(ValidationError, match="must be distinct"):
        FailedSaveTimedEffect(
            effect_id="charmed",
            additional_effect_ids=["incapacitated", "charmed"],
        )

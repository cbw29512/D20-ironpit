from __future__ import annotations

from app.combat.condition_removal import resolve_condition_removal
from app.combat.conditions import attack_roll_condition_sources
from app.combat.death_saves import resolve_death_save
from app.combat.defensive_spell_resolution import resolve_defensive_spell
from app.combat.effect_removal import choose_effect_removal_action, resolve_effect_removal
from app.combat.healing import resolve_healing
from app.combat.modifier_stack import add_modifier
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.state import build_combatant_state
from app.combat.targeting_wards import check_targeting_ward
from app.combat.timed_conditions import apply_timed_condition
from app.combat.dice import FixedDiceProvider
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import ResourceDefinition
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def _slot(member: EncounterCombatant, level: int):
    return next(item for item in member.state.resources if item.id == f"spell-slot-{level}")


def _spell(member: EncounterCombatant, spell_id: str):
    return next(item for item in member.state.template.defensive_spell_actions if item.id == spell_id)


def _setup(level: int) -> tuple[EncounterSetup, EncounterCombatant, EncounterCombatant]:
    paladin = _member(build_aurelia_brightshield_2014(level), "aurelia", "heroes", 0)
    ally = _member(build_kael_stillwater_2014(1), "kael", "heroes", 5)
    enemy = _member(build_commoner().model_copy(update={"ruleset": "2014"}), "enemy", "monsters", 10)
    setup = EncounterSetup(
        heroes=[paladin, ally], monsters=[enemy], hero_total_levels=level + 1,
        monster_total_cr="0", ruleset="2014",
    )
    return setup, paladin, ally


def test_protection_from_evil_good_filters_attack_and_condition_source_type() -> None:
    setup, paladin, ally = _setup(3)
    spell = _spell(paladin, "protection-from-evil-and-good")
    resolve_defensive_spell(1, paladin, [ally], spell, 1, _slot(paladin, 1), [m.state for m in [*setup.heroes, *setup.monsters]])

    fiend = _member(
        build_commoner().model_copy(update={"ruleset": "2014", "creature_type": "Fiend"}),
        "fiend", "monsters", 10,
    )
    humanoid = _member(
        build_commoner().model_copy(update={"ruleset": "2014", "creature_type": "Humanoid"}),
        "humanoid", "monsters", 10,
    )
    assert attack_roll_condition_sources(fiend.state, ally.state, 5)[1] == 1
    assert attack_roll_condition_sources(humanoid.state, ally.state, 5)[1] == 0
    assert apply_timed_condition(
        ally.state, "charmed", fiend.combatant_id, source_template=fiend.state.template,
    ) is None
    assert apply_timed_condition(
        ally.state, "charmed", humanoid.combatant_id, source_template=humanoid.state.template,
    ) == "charmed"


def test_sanctuary_gate_fails_closed_and_ends_when_owner_attacks() -> None:
    setup, paladin, ally = _setup(3)
    spell = _spell(paladin, "sanctuary")
    resolve_defensive_spell(1, paladin, [ally], spell, 1, _slot(paladin, 1), [m.state for m in [*setup.heroes, *setup.monsters]])

    failed = check_targeting_ward(setup.monsters[0], ally, FixedDiceProvider([1]))
    assert failed is not None and failed.succeeded is False
    assert failed.gate.source_effect_id == "sanctuary"

    self_setup, self_paladin, _ = _setup(3)
    self_spell = _spell(self_paladin, "sanctuary")
    resolve_defensive_spell(
        1, self_paladin, [self_paladin], self_spell, 1, _slot(self_paladin, 1),
        [m.state for m in [*self_setup.heroes, *self_setup.monsters]],
    )
    assert any(item.source_effect_id == "sanctuary" for item in self_paladin.state.active_modifiers)
    assert check_targeting_ward(self_paladin, self_setup.monsters[0], FixedDiceProvider([20])) is None
    assert not any(item.source_effect_id == "sanctuary" for item in self_paladin.state.active_modifiers)


def test_2014_lesser_restoration_uses_action_and_level_two_slot() -> None:
    _, paladin, ally = _setup(5)
    action = next(item for item in paladin.state.template.condition_removal_actions if item.id == "lesser-restoration")
    ally.state.active_effect_ids.append("poisoned")
    before = _slot(paladin, 2).current_uses

    event = resolve_condition_removal(1, 1, paladin, ally, action, ["poisoned"], "1:aurelia")

    assert action.action_cost == "action"
    assert event.removed_condition_ids == ["poisoned"]
    assert paladin.state.action_available is False
    assert _slot(paladin, 2).current_uses == before - 1


def test_beacon_of_hope_grants_wisdom_and_death_save_advantage_and_max_healing() -> None:
    setup, paladin, ally = _setup(9)
    beacon = _spell(paladin, "beacon-of-hope")
    resolve_defensive_spell(1, paladin, [ally], beacon, 3, _slot(paladin, 3), [m.state for m in [*setup.heroes, *setup.monsters]])

    assert saving_throw_mode(ally.state, "wisdom").value == "advantage"
    ally.state.current_hp = 0
    ally.state.is_unconscious = True
    death = resolve_death_save(2, 1, ally.combatant_id, ally.state, FixedDiceProvider([2, 15]))
    assert death.death_save_roll.mode.value == "advantage"
    assert death.death_save_roll.selected_roll == 15

    ally.state.current_hp = 1
    ally.state.is_unconscious = False
    cure = next(item for item in paladin.state.template.healing_actions if item.id == "cure-wounds")
    heal = resolve_healing(3, 1, paladin, ally, cure, FixedDiceProvider([1]), "1:aurelia")
    assert heal.healing_roll.rolls == [8]
    assert heal.healing_roll.total == 11


def _level_four_buff_source() -> EncounterCombatant:
    base = build_commoner().model_copy(update={
        "ruleset": "2014",
        "ability_scores": build_aurelia_brightshield_2014(9).ability_scores,
        "defensive_spell_actions": [DefensiveSpellAction(
            id="test-level-four-ward", name="Test Level Four Ward", level=4,
            range_ft=5, duration_minutes=1,
            modifier_effects=[SpellModifierEffect(kind="armor-class", flat_bonus=1)],
        )],
        "resources": [ResourceDefinition(id="spell-slot-4", name="Level 4 Spell Slot", max_uses=1)],
    })
    source = _member(base, "source", "monsters", 10)
    add_modifier(source.state, CombatModifier(
        id="source:test-level-four-ward:source:0", source_id="source",
        source_effect_id="test-level-four-ward", kind=ModifierKind.ARMOR_CLASS,
        flat_bonus=1, target_id="source",
    ))
    return source


def test_dispel_magic_auto_removes_low_level_effect_and_checks_higher_level_effect() -> None:
    remover = _member(build_aurelia_brightshield_2014(9), "aurelia", "heroes", 0)
    low = _member(build_aurelia_brightshield_2014(3), "low", "monsters", 10)
    low_spell = _spell(low, "sanctuary")
    resolve_defensive_spell(1, low, [low], low_spell, 1, _slot(low, 1), [remover.state, low.state])
    setup = EncounterSetup(
        heroes=[remover], monsters=[low], hero_total_levels=9, monster_total_cr="3", ruleset="2014",
    )
    choice = choose_effect_removal_action(remover, setup, "1:aurelia")
    assert choice is not None
    event = resolve_effect_removal(2, 1, remover, setup, *choice, FixedDiceProvider([1]), "1:aurelia")
    assert event.check_dc is None
    assert event.removed_condition_ids == ["sanctuary"]
    assert not low.state.active_modifiers

    remover2 = _member(build_aurelia_brightshield_2014(9), "aurelia-2", "heroes", 0)
    high = _level_four_buff_source()
    setup2 = EncounterSetup(
        heroes=[remover2], monsters=[high], hero_total_levels=9, monster_total_cr="0", ruleset="2014",
    )
    choice2 = choose_effect_removal_action(remover2, setup2, "1:aurelia-2")
    assert choice2 is not None
    failed = resolve_effect_removal(1, 1, remover2, setup2, *choice2, FixedDiceProvider([1]), "1:aurelia-2")
    assert failed.check_dc == 14 and failed.check_succeeded is False
    assert high.state.active_modifiers

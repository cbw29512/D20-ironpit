import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.offensive_spell_effects import build_guiding_bolt
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(combatant_id: str, side: str, position: int, *, caster: bool = False, armor_class: int = 10):
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"
    template.name = combatant_id
    template.armor_class = armor_class
    if caster:
        template.spell_attack_actions = [build_guiding_bolt(5)]
        template.resources = [ResourceDefinition(id="spell-slot-1", name="Level 1 Slot", max_uses=1)]
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(target_ac: int = 10):
    caster = _member("caster", "heroes", 0, caster=True)
    ally = _member("ally", "heroes", 5)
    target = _member("target", "monsters", 30, armor_class=target_ac)
    setup = EncounterSetup(heroes=[caster, ally], monsters=[target], hero_total_levels=2, monster_total_cr="1")
    return setup, caster, ally, target


def test_guiding_bolt_hit_deals_radiant_damage_and_marks_next_attack() -> None:
    setup, caster, ally, target = _setup()
    spell = caster.state.template.spell_attack_actions[0]

    event = resolve_spell_attack(
        1, 1, caster, target, spell, setup, "1:caster",
        FixedDiceProvider([15, 6, 5, 4, 3]),
    )

    assert event.hit is True and event.critical is False
    assert event.attack_roll is not None and event.attack_roll.mode.value == "normal"
    assert event.damage_roll is not None and event.damage_roll.total == 18
    assert event.damage_components[0].damage_type.value == "radiant"
    assert event.feature_id == "guiding-bolt"
    assert caster.state.action_available is False
    assert next(item for item in caster.state.resources if item.id == "spell-slot-1").current_uses == 0

    assert len(target.state.active_modifiers) == 1
    rider = target.state.active_modifiers[0]
    assert rider.source_effect_id == "guiding-bolt"
    assert rider.consume_on_attack_against is True
    assert rider.expires_source_turn_end_round == 2

    target.state.template.armor_class = 30
    ally_attack = resolve_attack(
        2, 1, ally.state, target.state, ally.state.template.weapon_attack, 5,
        FixedDiceProvider([5, 15]), spend_action=False,
    )
    assert ally_attack.attack_roll is not None and ally_attack.attack_roll.mode.value == "advantage"
    assert target.state.active_modifiers == []


def test_guiding_bolt_miss_spends_slot_but_does_not_apply_advantage() -> None:
    setup, caster, _, target = _setup(target_ac=30)
    spell = caster.state.template.spell_attack_actions[0]

    event = resolve_spell_attack(
        1, 1, caster, target, spell, setup, "1:caster",
        FixedDiceProvider([10]),
    )

    assert event.hit is False
    assert event.damage_roll is None
    assert target.state.active_modifiers == []
    assert caster.state.action_available is False
    assert next(item for item in caster.state.resources if item.id == "spell-slot-1").current_uses == 0


def test_guiding_bolt_uses_ranged_attack_disadvantage_in_close_combat() -> None:
    setup, caster, _, target = _setup(target_ac=30)
    target.position_ft = 5
    spell = caster.state.template.spell_attack_actions[0]

    event = resolve_spell_attack(
        1, 1, caster, target, spell, setup, "1:caster",
        FixedDiceProvider([18, 2]),
    )

    assert event.attack_roll is not None and event.attack_roll.mode.value == "disadvantage"
    assert event.attack_roll.selected_roll == 2


def test_guiding_bolt_does_not_use_higher_slot_while_upcasting_is_deferred() -> None:
    setup, caster, _, target = _setup()
    caster.state.resources = [
        item.model_copy(update={"id": "spell-slot-2", "name": "Level 2 Slot", "current_uses": 1, "max_uses": 1})
        for item in caster.state.resources
    ]
    spell = caster.state.template.spell_attack_actions[0]

    with pytest.raises(ValueError, match="No level 1 spell slot"):
        resolve_spell_attack(1, 1, caster, target, spell, setup, "1:caster", FixedDiceProvider([20]))
    assert caster.state.resources[0].current_uses == 1
    assert caster.state.action_available is True

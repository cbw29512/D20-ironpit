from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.audited_fighter import build_karnok_stoneward
from app.content.healing_spell_effects import build_cure_wounds
from app.content.offensive_spell_effects import build_guiding_bolt
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(combatant_id: str, side: str, position: int, *, caster: bool = False, armor_class: int = 10):
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"
    template.name = combatant_id
    template.armor_class = armor_class
    template.resources = []
    if caster:
        template.spell_attack_actions = [build_guiding_bolt(5)]
        template.resources = [ResourceDefinition(id="spell-slot-1", name="Level 1 Slot", max_uses=2)]
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_live_turn_uses_guiding_bolt_before_weapon_fallback() -> None:
    caster = _member("caster", "heroes", 0, caster=True)
    target = _member("target", "monsters", 30)
    setup = EncounterSetup(heroes=[caster], monsters=[target], hero_total_levels=1, monster_total_cr="1")

    events, sequence = resolve_combat_turn(
        1, 1, caster, target, setup,
        FixedDiceProvider([15, 6, 5, 4, 3]),
    )

    assert sequence == 2
    assert len(events) == 1
    assert events[0].feature_id == "guiding-bolt"
    assert events[0].hit is True
    assert events[0].damage_roll is not None and events[0].damage_roll.total == 18
    assert caster.state.resources[0].current_uses == 1


def test_live_turn_rescues_zero_hp_ally_before_offensive_spell_attack() -> None:
    caster = _member("caster", "heroes", 0, caster=True)
    caster.state.template.healing_actions = [build_cure_wounds(3)]
    ally = _member("ally", "heroes", 5)
    target = _member("target", "monsters", 30)
    setup = EncounterSetup(heroes=[caster, ally], monsters=[target], hero_total_levels=2, monster_total_cr="1")
    ally.state.resources = []
    apply_damage(ally.state, ally.state.current_hp)

    events, _ = resolve_combat_turn(
        1, 1, caster, target, setup,
        FixedDiceProvider([8, 7]),
    )

    assert events[0].feature_id == "cure-wounds"
    assert events[0].event_type == "healing"
    assert ally.state.current_hp > 0
    assert all(event.feature_id != "guiding-bolt" for event in events)
    assert caster.state.resources[0].current_uses == 1

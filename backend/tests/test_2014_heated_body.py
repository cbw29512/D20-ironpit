from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.monster_catalog_2014 import monster_by_id_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def test_azer_heated_traits_compile_from_source_data() -> None:
    azer = monster_by_id_2014("azer")
    assert len(azer.melee_hit_reactive_damage) == 1
    heated = azer.melee_hit_reactive_damage[0]
    assert (heated.range_ft, heated.dice_count, heated.dice_size, heated.damage_type.value) == (5, 1, 10, "fire")
    assert any(part.damage_type.value == "fire" for part in azer.weapon_attack.on_hit_damage)


def test_melee_hit_inside_range_applies_heated_body_to_attacker() -> None:
    attacker = EncounterCombatant(
        combatant_id="hero-1", side="heroes", position_ft=5,
        state=build_combatant_state(build_demo_fighter()),
    )
    defender = EncounterCombatant(
        combatant_id="monster-1", side="monsters", position_ft=10,
        state=build_combatant_state(monster_by_id_2014("azer")),
    )
    setup = EncounterSetup(heroes=[attacker], monsters=[defender], hero_total_levels=1, monster_total_cr="2")
    begin_turn(attacker.state)
    before = attacker.state.current_hp
    event = resolve_encounter_attack(
        1, 1, attacker, defender, attacker.state.template.weapon_attack, 5,
        FixedDiceProvider([20, 4, 7, 7]), setup,
    )
    assert event.hit is True
    assert event.actor_hp_before == before
    assert event.actor_hp_after == before - 7
    assert event.reactive_damage_roll is not None and event.reactive_damage_roll.total == 7
    assert event.reactive_damage_components[0].damage_type.value == "fire"

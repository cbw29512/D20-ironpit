from app.combat.attacks import resolve_attack
from app.combat.barbarian_level2 import reckless_attack_active
from app.combat.condition_lifecycle import resolve_source_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.domain.encounters import EncounterCombatant, EncounterSetup


def test_barbarian2_snapshot_has_exact_level_features() -> None:
    template = build_rokhan_stonefury_level(2)
    assert template.max_hp == 23
    assert template.progression_features.danger_sense is True
    assert template.progression_features.reckless_attack is True
    assert template.weapon_attack.attack_ability == "strength"
    assert template.alternate_weapon_attacks[0].attack_ability == "strength"


def test_danger_sense_grants_dexterity_save_advantage() -> None:
    state = build_combatant_state(build_rokhan_stonefury_level(2))
    roll, succeeded = resolve_saving_throw(state, "dexterity", 12, FixedDiceProvider([2, 15]))
    assert roll is not None
    assert roll.mode == "advantage"
    assert roll.rolls == [2, 15]
    assert roll.selected_roll == 15
    assert succeeded is True


def test_danger_sense_and_restrained_cancel_to_normal() -> None:
    state = build_combatant_state(build_rokhan_stonefury_level(2))
    state.active_effect_ids.append("restrained")
    roll, _ = resolve_saving_throw(state, "dexterity", 12, FixedDiceProvider([10]))
    assert roll is not None
    assert roll.mode == "normal"
    assert roll.rolls == [10]


def _reckless_setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    hero = EncounterCombatant(
        combatant_id="hero-1:rokhan-stonefury-l2", side="heroes", position_ft=5,
        state=build_combatant_state(build_rokhan_stonefury_level(2)),
    )
    enemy = EncounterCombatant(
        combatant_id="monster-1:test-fighter", side="monsters", position_ft=10,
        state=build_combatant_state(build_karnok_stoneward()),
    )
    return hero, enemy, EncounterSetup(heroes=[hero], monsters=[enemy], hero_total_levels=2, monster_total_cr="0")


def test_reckless_attack_grants_both_sides_advantage_until_next_turn() -> None:
    rokhan, fighter, setup = _reckless_setup()
    fighter.state.template.armor_class = 99
    attack = resolve_encounter_attack(
        1, 1, rokhan, fighter, rokhan.state.template.weapon_attack, 5,
        FixedDiceProvider([2, 15]), setup, allow_reckless=True,
    )
    assert attack.attack_roll is not None
    assert attack.attack_roll.mode == "advantage"
    assert attack.attack_roll.rolls == [2, 15]
    assert attack.feature_id == "reckless-attack"
    assert reckless_attack_active(rokhan.state) is True

    rokhan.state.template.armor_class = 99
    counter = resolve_attack(
        2, 1, fighter.state, rokhan.state, fighter.state.template.weapon_attack, 5,
        FixedDiceProvider([3, 14]), actor_event_id=fighter.combatant_id,
    )
    assert counter.attack_roll is not None
    assert counter.attack_roll.mode == "advantage"
    assert counter.attack_roll.rolls == [3, 14]

    events, _ = resolve_source_condition_timing(3, 2, rokhan, setup, "source_turn_start")
    assert reckless_attack_active(rokhan.state) is False
    assert any(event.feature_id == "reckless-attack" for event in events)


def test_reaction_style_generic_attack_cannot_start_reckless() -> None:
    rokhan = build_combatant_state(build_rokhan_stonefury_level(2))
    fighter = build_combatant_state(build_karnok_stoneward())
    fighter.template.armor_class = 99
    event = resolve_attack(
        1, 1, rokhan, fighter, rokhan.template.weapon_attack, 5,
        FixedDiceProvider([10]), actor_event_id="hero-1:rokhan-stonefury-l2", spend_action=False,
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode == "normal"
    assert event.attack_roll.rolls == [10]
    assert reckless_attack_active(rokhan) is False

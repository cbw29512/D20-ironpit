from app.combat.attacks import resolve_attack
from app.combat.conditions import attack_roll_condition_sources
from app.combat.death_saves import resolve_death_save
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import RollMode


def _downed_character():
    state = build_combatant_state(build_demo_fighter())
    assert apply_damage(state, state.current_hp) == "unconscious"
    return state


def test_monster_dies_at_zero_hp_by_default() -> None:
    state = build_combatant_state(build_goblin_warrior())
    outcome = apply_damage(state, state.current_hp)
    assert outcome == "dead"
    assert state.current_hp == 0
    assert state.is_dead is True
    assert state.is_alive is False


def test_character_at_zero_is_unconscious_prone_but_alive() -> None:
    state = _downed_character()
    assert state.current_hp == 0
    assert state.is_alive is True
    assert state.is_unconscious is True
    assert state.is_dead is False
    assert "prone" in state.active_effect_ids


def test_becoming_unconscious_ends_dodge_benefit() -> None:
    state = build_combatant_state(build_demo_fighter())
    state.active_effect_ids.append("dodge")
    apply_damage(state, state.current_hp)
    assert "dodge" not in state.active_effect_ids
    assert "prone" in state.active_effect_ids


def test_unconscious_prone_cancels_attack_advantage_from_beyond_five_feet() -> None:
    attacker = build_combatant_state(build_goblin_warrior())
    defender = _downed_character()
    advantage, disadvantage = attack_roll_condition_sources(attacker, defender, 30)
    assert advantage > 0
    assert disadvantage > 0


def test_massive_damage_can_kill_character_instantly() -> None:
    state = build_combatant_state(build_demo_fighter())
    damage = state.current_hp + state.template.max_hp
    assert apply_damage(state, damage) == "dead"
    assert state.is_dead is True
    assert state.is_alive is False


def test_damage_at_zero_adds_failures_and_critical_adds_two() -> None:
    state = _downed_character()
    apply_damage(state, 1)
    assert state.death_save_failures == 1
    apply_damage(state, 1, critical=True)
    assert state.is_dead is True
    assert state.death_save_failures == 3


def test_temporary_hp_does_not_prevent_damage_failure_at_zero() -> None:
    state = _downed_character()
    state.temporary_hp = 5
    apply_damage(state, 1)
    assert state.temporary_hp == 4
    assert state.current_hp == 0
    assert state.death_save_failures == 1


def test_temporary_hp_does_not_prevent_critical_damage_failures_at_zero() -> None:
    state = _downed_character()
    state.temporary_hp = 20
    apply_damage(state, 1, critical=True)
    assert state.temporary_hp == 19
    assert state.death_save_failures == 2
    assert state.is_dead is False


def test_damage_at_zero_equal_to_max_hp_kills_immediately() -> None:
    state = _downed_character()
    apply_damage(state, state.template.max_hp)
    assert state.is_dead is True


def test_temporary_hp_does_not_prevent_instant_death_at_zero() -> None:
    state = _downed_character()
    state.temporary_hp = state.template.max_hp
    apply_damage(state, state.template.max_hp)
    assert state.is_dead is True


def test_close_hit_on_unconscious_character_has_advantage_and_is_critical() -> None:
    defender = _downed_character()
    attacker = build_combatant_state(build_goblin_warrior())
    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([19, 19, 1, 1, 1, 1]),
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.selected_roll == 19
    assert event.hit is True
    assert event.critical is True
    assert defender.death_save_failures == 2
    assert defender.is_dead is False


def test_natural_one_on_death_save_counts_as_two_failures() -> None:
    state = _downed_character()
    event = resolve_death_save(1, 1, "hero-1", state, FixedDiceProvider([1]))
    assert state.death_save_failures == 2
    assert state.is_dead is False
    assert event.death_save_roll is not None
    assert event.death_save_roll.total == 1


def test_natural_twenty_restores_one_hp_resets_saves_and_leaves_prone() -> None:
    state = _downed_character()
    state.death_save_successes = 2
    state.death_save_failures = 1
    event = resolve_death_save(1, 1, "hero-1", state, FixedDiceProvider([20]))
    assert state.current_hp == 1
    assert state.is_unconscious is False
    assert "prone" in state.active_effect_ids
    assert state.death_save_successes == 0
    assert state.death_save_failures == 0
    assert event.hp_after == 1


def test_three_successes_make_character_stable_and_reset_trackers() -> None:
    state = _downed_character()
    for sequence in range(1, 4):
        resolve_death_save(sequence, sequence, "hero-1", state, FixedDiceProvider([10]))
    assert state.current_hp == 0
    assert state.is_stable is True
    assert state.is_unconscious is True
    assert state.death_save_successes == 0
    assert state.death_save_failures == 0


def test_three_failures_kill_character() -> None:
    state = _downed_character()
    for sequence in range(1, 4):
        resolve_death_save(sequence, sequence, "hero-1", state, FixedDiceProvider([9]))
    assert state.is_dead is True
    assert state.is_alive is False

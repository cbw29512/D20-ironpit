from __future__ import annotations

from app.combat.cleave import cleave_attack_profile, select_cleave_target
from app.combat.dice import FixedDiceProvider
from app.combat.standard_attack_action import resolve_standard_attack_action
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.content.weapon_catalog import build_weapon
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _attacker(*, mastered: bool = True, position: int = 0):
    template = build_karnok_stoneward().model_copy(
        update={"weapon_masteries": ["greataxe"] if mastered else [], "combat_traits": []},
        deep=True,
    )
    state = build_combatant_state(template)
    attack = state.template.weapon_attack.model_copy(
        update={
            "id": "cleave-greataxe", "weapon": build_weapon("greataxe"),
            "attack_ability_modifier": 3, "damage_bonus": 3,
        },
        deep=True,
    )
    return EncounterCombatant(combatant_id="hero-1", side="heroes", position_ft=position, state=state), attack


def _target(target_id: str, position: int) -> EncounterCombatant:
    source = build_goblin_warrior()
    template = source.model_copy(update={"armor_class": 10, "max_hp": 40}, deep=True)
    return EncounterCombatant(
        combatant_id=target_id, side="monsters", position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(attacker, targets) -> EncounterSetup:
    return EncounterSetup(
        heroes=[attacker], monsters=list(targets), hero_total_levels=1, monster_total_cr="1/2",
    )


def test_cleave_hit_attacks_second_enemy_and_removes_positive_ability_damage() -> None:
    attacker, attack = _attacker()
    first, second = _target("monster-1", 5), _target("monster-2", 5)
    setup = _setup(attacker, [first, second])

    events, sequence = resolve_standard_attack_action(
        1, 1, attacker, first, attack, 5, FixedDiceProvider([15, 7, 14, 6]), setup, "1:hero-1",
    )

    assert sequence == 3
    assert len(events) == 2
    assert events[0].target_id == "monster-1"
    assert events[0].damage_roll is not None and events[0].damage_roll.total == 10
    assert events[1].target_id == "monster-2"
    assert events[1].feature_id == "weapon-mastery-cleave"
    assert events[1].damage_roll is not None and events[1].damage_roll.total == 6
    assert "Cleave makes the once-per-turn extra attack" in events[1].description


def test_cleave_is_once_per_turn_even_across_another_attack_action() -> None:
    attacker, attack = _attacker()
    first, second = _target("monster-1", 5), _target("monster-2", 5)
    setup = _setup(attacker, [first, second])

    first_events, sequence = resolve_standard_attack_action(
        1, 1, attacker, first, attack, 5, FixedDiceProvider([15, 7, 14, 6]), setup, "1:hero-1",
    )
    attacker.state.action_available = True
    second_events, sequence = resolve_standard_attack_action(
        sequence, 1, attacker, first, attack, 5, FixedDiceProvider([15, 5]), setup, "1:hero-1",
    )

    assert len(first_events) == 2
    assert len(second_events) == 1
    assert sequence == 4


def test_cleave_requires_triggering_hit_and_selected_mastery() -> None:
    attacker, attack = _attacker()
    first, second = _target("monster-1", 5), _target("monster-2", 5)
    setup = _setup(attacker, [first, second])

    missed, _ = resolve_standard_attack_action(
        1, 1, attacker, first, attack, 5, FixedDiceProvider([2]), setup, "1:hero-1",
    )
    unmastered, unmastered_attack = _attacker(mastered=False)
    setup2 = _setup(unmastered, [_target("monster-3", 5), _target("monster-4", 5)])
    events, _ = resolve_standard_attack_action(
        1, 1, unmastered, setup2.monsters[0], unmastered_attack, 5,
        FixedDiceProvider([15, 7]), setup2, "1:hero-1",
    )

    assert len(missed) == 1 and missed[0].hit is False
    assert len(events) == 1


def test_cleave_requires_second_target_within_first_target_five_feet_and_weapon_reach() -> None:
    attacker, attack = _attacker()
    first, second = _target("monster-1", 10), _target("monster-2", 0)
    extended = attack.model_copy(update={"weapon": attack.weapon.model_copy(update={"reach_ft": 10})}, deep=True)
    setup = _setup(attacker, [first, second])

    assert select_cleave_target(attacker, first, extended, setup) is None

    first.position_ft = 5
    assert select_cleave_target(attacker, first, attack, setup) is second


def test_cleave_damage_profile_preserves_nonability_bonus_and_negative_modifier() -> None:
    _, attack = _attacker()
    enhanced = attack.model_copy(update={"damage_bonus": 5, "attack_ability_modifier": 3}, deep=True)
    penalized = attack.model_copy(update={"damage_bonus": -1, "attack_ability_modifier": -1}, deep=True)

    assert cleave_attack_profile(enhanced).damage_bonus == 2
    assert cleave_attack_profile(penalized).damage_bonus == -1

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.formation import starting_position_ft
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.encounters import EncounterCombatant
from app.domain.models import RollMode, WeaponAttackKind


def _member(combatant_id: str, side: str, template) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=starting_position_ft(template, side),
        state=build_combatant_state(template),
    )


def test_natural_twenty_critical_uses_canonical_encounter_attack() -> None:
    fighter = _member("hero-1", "heroes", build_demo_fighter())
    goblin = _member("monster-1", "monsters", build_goblin_warrior())

    event = resolve_encounter_attack(
        1, 1, fighter, goblin, fighter.state.template.weapon_attack,
        combatant_distance(fighter, goblin), FixedDiceProvider([20, 7, 6]), None,
    )

    assert event.critical is True
    assert event.damage_roll is not None and event.damage_roll.total == 16
    assert goblin.state.current_hp == 0


def test_natural_one_always_misses_in_canonical_encounter_attack() -> None:
    fighter = _member("hero-1", "heroes", build_demo_fighter())
    goblin = _member("monster-1", "monsters", build_goblin_warrior())

    event = resolve_encounter_attack(
        1, 1, goblin, fighter, goblin.state.template.weapon_attack,
        combatant_distance(goblin, fighter), FixedDiceProvider([1]), None,
    )

    assert event.attack_roll is not None and event.attack_roll.rolls == [1]
    assert event.hit is False
    assert fighter.state.current_hp == fighter.state.template.max_hp


def test_demo_templates_use_fixed_five_foot_melee_formation() -> None:
    fighter = _member("hero-1", "heroes", build_demo_fighter())
    goblin = _member("monster-1", "monsters", build_goblin_warrior())

    assert combatant_distance(fighter, goblin) == 5
    assert goblin.state.template.weapon_attack.weapon.attack_kind is WeaponAttackKind.MELEE
    assert goblin.state.template.alternate_weapon_attacks[0].weapon.attack_kind is WeaponAttackKind.RANGED

    event = resolve_encounter_attack(
        1, 1, fighter, goblin, fighter.state.template.weapon_attack,
        5, FixedDiceProvider([10, 4]), None,
    )
    assert event.attack_roll is not None and event.attack_roll.mode is RollMode.NORMAL

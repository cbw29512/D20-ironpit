from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.redirect_attack import select_redirect_ally
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.monster_goblin_boss import build_goblin_boss
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(combatant_id, side, position, template):
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def _ranged_setup(ally_position: int = 25):
    attacker = _member("hero-1", "heroes", 0, build_goblin_warrior())
    boss = _member("boss-1", "monsters", 20, build_goblin_boss())
    ally = _member("goblin-1", "monsters", ally_position, build_goblin_warrior())
    setup = EncounterSetup(
        heroes=[attacker], monsters=[boss, ally], hero_total_levels=1, monster_total_cr="1.25",
    )
    return attacker, boss, ally, setup


def _melee_setup():
    attacker = _member("hero-1", "heroes", 0, build_demo_fighter())
    boss = _member("boss-1", "monsters", 5, build_goblin_boss())
    ally = _member("goblin-1", "monsters", 10, build_goblin_warrior())
    setup = EncounterSetup(
        heroes=[attacker], monsters=[boss, ally], hero_total_levels=1, monster_total_cr="1.25",
    )
    return attacker, boss, ally, setup


def test_redirect_uses_same_roll_against_ally_ac_and_swaps_positions() -> None:
    attacker, boss, ally, setup = _ranged_setup()
    boss_hp, ally_hp = boss.state.current_hp, ally.state.current_hp
    attack = attacker.state.template.alternate_weapon_attacks[0]

    event = resolve_encounter_attack(
        1, 1, attacker, boss, attack, 20, FixedDiceProvider([11, 4]), setup,
    )

    assert event.attack_roll is not None and event.attack_roll.selected_roll == 11
    assert event.attack_roll.total == 15
    assert event.target_id == ally.combatant_id
    assert event.hit is True
    assert boss.state.current_hp == boss_hp
    assert ally.state.current_hp < ally_hp
    assert boss.state.reaction_available is False
    assert (boss.position_ft, ally.position_ft) == (25, 20)
    assert "uses Redirect Attack" in event.description


def test_redirect_declines_swap_that_would_provoke_opportunity_attack() -> None:
    _, boss, _, setup = _melee_setup()
    assert select_redirect_ally(boss, setup) is None
    assert boss.state.reaction_available is True


def test_redirect_requires_ally_within_five_feet() -> None:
    _, boss, _, setup = _ranged_setup(ally_position=30)
    assert select_redirect_ally(boss, setup) is None


def test_redirect_rejects_large_ally() -> None:
    _, boss, ally, setup = _ranged_setup()
    ally.state.template.size = "large"
    assert select_redirect_ally(boss, setup) is None


def test_redirect_requires_available_reaction() -> None:
    _, boss, _, setup = _ranged_setup()
    boss.state.reaction_available = False
    assert select_redirect_ally(boss, setup) is None


def test_blinded_goblin_boss_cannot_redirect_attack() -> None:
    _, boss, _, setup = _ranged_setup()
    boss.state.active_effect_ids.append("blinded")
    assert select_redirect_ally(boss, setup) is None

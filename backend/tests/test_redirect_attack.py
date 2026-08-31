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


def _setup(ally_position: int = 10):
    attacker = _member("hero-1", "heroes", 0, build_demo_fighter())
    boss = _member("boss-1", "monsters", 5, build_goblin_boss())
    ally = _member("goblin-1", "monsters", ally_position, build_goblin_warrior())
    setup = EncounterSetup(
        heroes=[attacker], monsters=[boss, ally], hero_total_levels=1, monster_total_cr="1.25",
    )
    return attacker, boss, ally, setup


def test_redirect_uses_same_roll_against_ally_ac_and_swaps_positions() -> None:
    attacker, boss, ally, setup = _setup()
    boss_hp, ally_hp = boss.state.current_hp, ally.state.current_hp

    event = resolve_encounter_attack(
        1, 1, attacker, boss, attacker.state.template.weapon_attack, 5,
        FixedDiceProvider([10, 4]), setup,
    )

    assert event.attack_roll is not None and event.attack_roll.selected_roll == 10
    assert event.attack_roll.total == 15
    assert event.target_id == ally.combatant_id
    assert event.hit is True
    assert boss.state.current_hp == boss_hp
    assert ally.state.current_hp < ally_hp
    assert boss.state.reaction_available is False
    assert (boss.position_ft, ally.position_ft) == (10, 5)
    assert "uses Redirect Attack" in event.description


def test_redirect_requires_ally_within_five_feet() -> None:
    _, boss, _, setup = _setup(ally_position=15)
    assert select_redirect_ally(boss, setup) is None


def test_redirect_rejects_large_ally() -> None:
    _, boss, ally, setup = _setup()
    ally.state.template.size = "large"
    assert select_redirect_ally(boss, setup) is None


def test_redirect_requires_available_reaction() -> None:
    _, boss, _, setup = _setup()
    boss.state.reaction_available = False
    assert select_redirect_ally(boss, setup) is None

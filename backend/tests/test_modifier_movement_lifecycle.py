from app.combat.concentration import start_concentration
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_movement import take_encounter_dash
from app.combat.modifier_stack import add_modifier
from app.combat.orc import use_adrenaline_rush
from app.combat.state import begin_turn, build_combatant_state
from app.combat.tactical_shift import resolve_tactical_shift
from app.content.audited_barbarian import build_rokhan_stonefury
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.content.fighter_progression import build_karnok_stoneward_level
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind


def _speed_modifier(source_id: str = "effect-source") -> CombatModifier:
    return CombatModifier(
        id=f"{source_id}-slow", source_id=source_id, source_effect_id="slow",
        kind=ModifierKind.SPEED, flat_bonus=-10,
    )


def _member(combatant_id, side, position, template):
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_dash_adds_effective_speed_not_base_speed() -> None:
    mover = _member("hero-1", "heroes", 0, build_karnok_stoneward())
    target = _member("monster-1", "monsters", 60, build_goblin_warrior())
    add_modifier(mover.state, _speed_modifier("encounter-source"))
    begin_turn(mover.state)

    event = take_encounter_dash(1, 1, mover, target)

    assert event.movement_ft == 20
    assert mover.state.movement_remaining_ft == 40


def test_adrenaline_rush_keeps_resource_and_temp_hp_but_abstracts_dash_movement() -> None:
    state = build_combatant_state(build_karnok_stoneward())
    add_modifier(state, _speed_modifier())
    begin_turn(state)
    movement_before = state.movement_remaining_ft

    event = use_adrenaline_rush(1, 1, state, "hero-1")

    assert event is not None and event.movement_ft == 0
    assert state.movement_remaining_ft == movement_before
    assert state.temporary_hp == 2


def test_tactical_shift_is_arena_neutral_under_fixed_formation() -> None:
    hero = _member("hero-1", "heroes", 0, build_karnok_stoneward_level(5))
    monster = _member("monster-1", "monsters", 35, build_goblin_warrior())
    setup = EncounterSetup(heroes=[hero], monsters=[monster], hero_total_levels=5, monster_total_cr="1/4")
    add_modifier(hero.state, _speed_modifier())

    event = resolve_tactical_shift(1, 1, hero, setup)

    assert event is None
    assert hero.position_ft == 0


def test_failed_concentration_save_from_encounter_attack_cleans_ally_modifier() -> None:
    owner = _member("hero-1", "heroes", 0, build_karnok_stoneward())
    ally = _member("hero-2", "heroes", 0, build_rokhan_stonefury())
    attacker = _member("monster-1", "monsters", 5, build_goblin_warrior())
    setup = EncounterSetup(
        heroes=[owner, ally], monsters=[attacker], hero_total_levels=2, monster_total_cr="1/4",
    )
    start_concentration(owner.state, owner.combatant_id, "bless", 1, [owner.state, ally.state, attacker.state])
    add_modifier(ally.state, CombatModifier(
        id="ally-bless-save", source_id=owner.combatant_id, source_effect_id="bless",
        kind=ModifierKind.SAVING_THROW_BONUS_DIE, dice_count=1, dice_size=4,
        concentration_required=True,
    ))

    event = resolve_encounter_attack(
        1, 1, attacker, owner, attacker.state.template.weapon_attack, 5,
        FixedDiceProvider([19, 1, 1]), setup,
    )

    assert event.hit is True
    assert owner.state.concentration is None
    assert ally.state.active_modifiers == []

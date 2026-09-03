from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_initiative import roll_encounter_initiative
from app.combat.grapple import apply_grapple, resolve_escape_grapple
from app.combat.state import build_combatant_state
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id, side, position):
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_champion_level_three_snapshot_has_raw_hp_and_features() -> None:
    karnok = build_karnok_stoneward_level(3)
    features = karnok.progression_features
    assert (karnok.id, karnok.level, karnok.max_hp) == ("karnok-stoneward-l3", 3, 28)
    assert features.critical_hit_minimum == 19
    assert features.initiative_advantage is True
    assert features.athletics_advantage is True
    assert features.critical_move_fraction == 0.5


def test_improved_critical_makes_a_hitting_natural_nineteen_critical() -> None:
    attacker = build_combatant_state(build_karnok_stoneward_level(3))
    defender = build_combatant_state(build_commoner().model_copy(update={"max_hp": 100}))
    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([19, 1, 1, 1, 1, 1, 1, 1, 1]),
    )
    assert event.hit is True
    assert event.critical is True
    assert event.attack_roll.selected_roll == 19


def test_improved_critical_does_not_make_natural_nineteen_an_automatic_hit() -> None:
    attacker = build_combatant_state(build_karnok_stoneward_level(3))
    defender = build_combatant_state(build_commoner().model_copy(update={"armor_class": 30, "max_hp": 100}))
    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([19]),
    )
    assert event.hit is False
    assert event.critical is False


def test_remarkable_athlete_grants_initiative_advantage() -> None:
    hero = _member(build_karnok_stoneward_level(3), "hero-1", "heroes", 5)
    monster = _member(build_commoner(), "monster-1", "monsters", 10)
    setup = EncounterSetup(heroes=[hero], monsters=[monster], hero_total_levels=3, monster_total_cr="0")
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([4, 17, 10]))
    hero_group = next(group for group in initiative.groups if group.side == "heroes")
    assert hero_group.natural_roll == 17
    assert hero_group.initiative_count == 18


def test_remarkable_athlete_grants_athletics_advantage_on_escape() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(3))
    apply_grapple(state, "monster-1", 15, 5, restrains=True)
    event = resolve_escape_grapple(1, 1, "hero-1", state, FixedDiceProvider([2, 15]))
    assert event.check_succeeded is True
    assert event.ability_check_roll.selected_roll == 15
    assert not state.grapple_sources


def test_remarkable_athlete_critical_move_is_arena_neutral_in_fixed_pit() -> None:
    hero = _member(build_karnok_stoneward_level(3), "hero-1", "heroes", 0)
    monster = _member(build_commoner().model_copy(update={"max_hp": 100}), "monster-1", "monsters", 20)
    setup = EncounterSetup(heroes=[hero], monsters=[monster], hero_total_levels=3, monster_total_cr="0")
    shortbow = hero.state.template.alternate_weapon_attacks[0]
    event = resolve_encounter_attack(
        1, 1, hero, monster, shortbow, 20,
        FixedDiceProvider([19, 1, 1, 1, 1]), setup,
    )
    assert event.critical is True
    assert event.movement_ft is None
    assert hero.position_ft == 0
    assert monster.state.reaction_available is True


def test_remarkable_athlete_never_uses_critical_move_to_kite() -> None:
    hero = _member(build_karnok_stoneward_level(3), "hero-1", "heroes", 5)
    monster = _member(build_commoner().model_copy(update={"max_hp": 100}), "monster-1", "monsters", 10)
    setup = EncounterSetup(heroes=[hero], monsters=[monster], hero_total_levels=3, monster_total_cr="0")
    event = resolve_encounter_attack(
        1, 1, hero, monster, hero.state.template.weapon_attack, 5,
        FixedDiceProvider([19, 1, 1, 1, 1, 1, 1, 1, 1]), setup,
    )
    assert event.critical is True
    assert event.movement_ft is None
    assert hero.position_ft == 5

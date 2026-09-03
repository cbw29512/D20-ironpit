from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_setup import build_encounter_setup
from app.combat.pit_policy import choose_standard_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monster_attacks import build_giant_lizard_attack
from app.content.monsters import build_giant_lizard
from app.content.pregens import build_mara_quickstep
from app.content.rogue_attacks import build_mara_shortbow_attack
from app.domain.models import EncounterSelection, RollMode, WeaponAttackKind


def _at_distance(setup, distance_ft: int):
    hero, monster = setup.heroes[0], setup.monsters[0]
    hero.position_ft = 0
    monster.position_ft = distance_ft
    return hero, monster


def _disable_adrenaline_rush(hero) -> None:
    resource = next(item for item in hero.state.resources if item.id == "adrenaline-rush")
    resource.current_uses = 0


def test_melee_only_creature_attacks_without_movement_or_dash() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-giant-lizard"],
    ))
    hero, monster = _at_distance(setup, 60)
    hero.state.template.alternate_weapon_attacks = []
    _disable_adrenaline_rush(hero)
    before = (hero.position_ft, monster.position_ft)

    events, _ = resolve_combat_turn(1, 1, hero, monster, setup, FixedDiceProvider([10, 1, 1]))

    assert any(event.event_type == "attack" for event in events)
    assert not any(event.event_type in {"movement", "dash"} for event in events)
    assert (hero.position_ft, monster.position_ft) == before


def test_frontline_with_backup_range_prefers_melee_under_fixed_formation() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-giant-lizard"],
    ))
    hero, monster = _at_distance(setup, 60)
    _disable_adrenaline_rush(hero)

    events, _ = resolve_combat_turn(1, 1, hero, monster, setup, FixedDiceProvider([10, 1, 1]))

    attack = next(event for event in events if event.event_type == "attack")
    assert attack.weapon_id == "greatsword"
    assert not any(event.event_type in {"movement", "dash"} for event in events)


def test_protected_ranged_primary_uses_range_without_close_combat_disadvantage() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "mara-quickstep-l1"],
        monster_ids=["srd-giant-lizard"],
    ))
    archer = setup.heroes[1]
    ranged = next(
        attack for attack in [archer.state.template.weapon_attack, *archer.state.template.alternate_weapon_attacks]
        if attack.weapon.attack_kind is WeaponAttackKind.RANGED
    )
    archer.state.template.weapon_attack = ranged
    begin_turn(archer.state)

    choice = choose_standard_attack(archer, setup)
    assert choice is not None
    target, attack, distance = choice
    assert attack.weapon.attack_kind is WeaponAttackKind.RANGED

    event = resolve_attack(
        1, 1, archer.state, target.state, attack, distance,
        FixedDiceProvider([10, 1]), close_enemy_active=False,
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.NORMAL


def test_exposed_ranged_primary_switches_to_melee_when_it_has_a_melee_option() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["mara-quickstep-l1"], monster_ids=["srd-giant-lizard"],
    ))
    archer = setup.heroes[0]
    ranged = next(
        attack for attack in [archer.state.template.weapon_attack, *archer.state.template.alternate_weapon_attacks]
        if attack.weapon.attack_kind is WeaponAttackKind.RANGED
    )
    melee = next(
        attack for attack in [archer.state.template.weapon_attack, *archer.state.template.alternate_weapon_attacks]
        if attack.weapon.attack_kind is WeaponAttackKind.MELEE
    )
    archer.state.template.weapon_attack = ranged
    archer.state.template.alternate_weapon_attacks = [melee]

    choice = choose_standard_attack(archer, setup)

    assert choice is not None
    assert choice[1].weapon.attack_kind is WeaponAttackKind.MELEE


def test_low_level_raw_close_ranged_penalty_remains_available_outside_pit_policy() -> None:
    attacker = build_combatant_state(build_mara_quickstep())
    defender = build_combatant_state(build_giant_lizard())

    event = resolve_attack(
        1, 1, attacker, defender, build_mara_shortbow_attack(), 5,
        FixedDiceProvider([15, 2]), close_enemy_active=True,
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.attack_roll.selected_roll == 2

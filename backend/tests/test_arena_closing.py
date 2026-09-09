from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_setup import build_encounter_setup
from app.combat.pit_policy import choose_standard_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.monsters import build_giant_lizard
from app.content.pregens import build_mara_quickstep
from app.content.rogue_attacks import build_mara_shortbow_attack
from app.domain.grid import GridPosition
from app.domain.models import EncounterSelection, RollMode, WeaponAttackKind


def _set_grid_distance(setup, distance_ft: int):
    hero, monster = setup.heroes[0], setup.monsters[0]
    hero.state.position = GridPosition(x=0, y=6)
    monster.state.position = GridPosition(x=distance_ft // 5, y=6)
    return hero, monster


def _disable_adrenaline_rush(hero) -> None:
    resource = next(item for item in hero.state.resources if item.id == "adrenaline-rush")
    resource.current_uses = 0


def test_melee_only_creature_dodges_when_speed_cannot_enable_offense() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-giant-lizard"],
    ))
    hero, monster = _set_grid_distance(setup, 60)
    hero.state.template.alternate_weapon_attacks = []
    _disable_adrenaline_rush(hero)
    before = hero.state.position.model_copy(deep=True)

    events, _ = resolve_combat_turn(1, 1, hero, monster, setup, FixedDiceProvider([2]))

    assert not any(event.event_type == "movement" for event in events)
    assert not any(event.event_type == "attack" for event in events)
    assert events[-1].feature_id == "dodge"
    assert hero.state.position == before
    assert "dodge" in hero.state.active_effect_ids


def test_frontline_with_backup_range_uses_legal_range_instead_of_fake_closing() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-giant-lizard"],
    ))
    hero, monster = _set_grid_distance(setup, 60)
    _disable_adrenaline_rush(hero)

    events, _ = resolve_combat_turn(1, 1, hero, monster, setup, FixedDiceProvider([2]))

    attack = next(event for event in events if event.event_type == "attack")
    assert attack.weapon_id == "shortbow"
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
        FixedDiceProvider([2]), close_enemy_active=False,
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.NORMAL


def test_engaged_ranged_primary_switches_to_melee_when_it_has_a_melee_option() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["mara-quickstep-l1"], monster_ids=["srd-giant-lizard"],
    ))
    archer, target = setup.heroes[0], setup.monsters[0]
    archer.state.position = GridPosition(x=7, y=6)
    target.state.position = GridPosition(x=8, y=6)
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

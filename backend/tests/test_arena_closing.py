from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_setup import build_encounter_setup
from app.combat.policy import select_weapon_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monster_attacks import build_giant_lizard_attack
from app.content.monsters import build_giant_lizard
from app.content.pregens import build_mara_quickstep
from app.content.rogue_attacks import build_mara_shortbow_attack, build_mara_shortsword_attack
from app.domain.models import EncounterSelection, RollMode


def _at_distance(setup, distance_ft: int):
    hero, monster = setup.heroes[0], setup.monsters[0]
    hero.position_ft = 0
    monster.position_ft = distance_ft
    return hero, monster


def _disable_adrenaline_rush(hero) -> None:
    resource = next(item for item in hero.state.resources if item.id == "adrenaline-rush")
    resource.current_uses = 0


def test_melee_only_creature_dodges_and_moves_when_melee_is_unreachable_this_turn() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-giant-lizard"],
    ))
    hero, monster = _at_distance(setup, 60)
    hero.state.template.alternate_weapon_attacks = []
    _disable_adrenaline_rush(hero)

    events, _ = resolve_combat_turn(1, 1, hero, monster, setup, FixedDiceProvider([10]))

    assert [event.event_type for event in events] == ["feature", "movement"]
    assert events[0].feature_id == "dodge"
    assert events[1].distance_after_ft == 30
    assert hero.state.action_available is False
    assert "dodge" in hero.state.active_effect_ids
    assert not any(event.event_type in {"attack", "dash"} for event in events)


def test_true_range_option_attacks_without_closing_while_separated() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-giant-lizard"],
    ))
    hero, monster = _at_distance(setup, 60)
    _disable_adrenaline_rush(hero)

    events, _ = resolve_combat_turn(1, 1, hero, monster, setup, FixedDiceProvider([10, 1, 1]))

    attacks = [event for event in events if event.event_type == "attack"]
    assert len(attacks) == 1
    assert attacks[0].weapon_id == "shortbow"
    assert not any(event.event_type == "movement" for event in events)
    assert abs(hero.position_ft - monster.position_ft) == 60


def test_backup_ranged_option_is_used_until_enemy_reaches_melee() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-giant-lizard"],
    ))
    hero, monster = _at_distance(setup, 10)
    _disable_adrenaline_rush(hero)

    events, _ = resolve_combat_turn(1, 1, hero, monster, setup, FixedDiceProvider([10, 4, 4]))

    assert [event.event_type for event in events] == ["attack"]
    assert events[0].weapon_id == "shortbow"
    assert abs(hero.position_ft - monster.position_ft) == 10


def test_dodge_imposes_attack_disadvantage_until_dodgers_next_turn() -> None:
    defender = build_combatant_state(build_karnok_stoneward())
    attacker = build_combatant_state(build_giant_lizard())
    defender.active_effect_ids.append("dodge")

    event = resolve_attack(
        1, 1, attacker, defender, build_giant_lizard_attack(), 5,
        FixedDiceProvider([15, 2]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.attack_roll.selected_roll == 2
    assert event.hit is False

    begin_turn(defender)
    assert "dodge" not in defender.active_effect_ids


def test_ranged_primary_uses_melee_option_once_enemy_is_adjacent() -> None:
    template = build_mara_quickstep().model_copy(update={
        "weapon_attack": build_mara_shortbow_attack(),
        "alternate_weapon_attacks": [build_mara_shortsword_attack()],
    })
    state = build_combatant_state(template)

    attack = select_weapon_attack(state, 5)

    assert attack is not None
    assert attack.weapon.name == "Shortsword"

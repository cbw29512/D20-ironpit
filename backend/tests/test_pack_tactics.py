from app.combat.ally_context import has_adjacent_active_ally, pack_tactics_active
from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import combatant_distance
from app.domain.models import CombatTrait, EncounterSelection, RollMode


def _rat_pack_setup(starting_distance_ft: int = 5):
    return build_encounter_setup(EncounterSelection(
        hero_ids=["aldric-vane-l1"],
        monster_ids=["srd-giant-rat", "srd-giant-rat"],
    ))


def test_giant_rat_is_marked_with_pack_tactics() -> None:
    setup = _rat_pack_setup()
    assert CombatTrait.PACK_TACTICS in setup.monsters[0].state.template.combat_traits


def test_any_active_ally_counts_as_adjacent_regardless_of_position() -> None:
    setup = _rat_pack_setup()
    attacker, ally = setup.monsters
    target = setup.heroes[0]

    ally.position_ft = 90
    assert has_adjacent_active_ally(attacker, setup) is True
    assert pack_tactics_active(attacker, target, setup) is True


def test_downed_or_unconscious_ally_does_not_count_as_adjacent() -> None:
    setup = _rat_pack_setup()
    attacker, ally = setup.monsters
    target = setup.heroes[0]

    ally.state.current_hp = 0
    ally.state.is_unconscious = True

    assert has_adjacent_active_ally(attacker, setup) is False
    assert pack_tactics_active(attacker, target, setup) is False


def test_incapacitated_ally_does_not_enable_pack_tactics() -> None:
    for condition in ("incapacitated", "paralyzed", "petrified", "stunned"):
        setup = _rat_pack_setup()
        attacker, ally = setup.monsters
        target = setup.heroes[0]
        ally.state.active_effect_ids.append(condition)
        assert has_adjacent_active_ally(attacker, setup) is False, condition
        assert pack_tactics_active(attacker, target, setup) is False, condition


def test_partial_debuffed_ally_still_counts_for_pack_tactics() -> None:
    setup = _rat_pack_setup()
    attacker, ally = setup.monsters
    target = setup.heroes[0]
    ally.state.active_effect_ids.append("poisoned")
    assert has_adjacent_active_ally(attacker, setup) is True
    assert pack_tactics_active(attacker, target, setup) is True


def test_single_combatant_side_has_no_adjacent_ally() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["aldric-vane-l1"],
        monster_ids=["srd-giant-rat"],
    ))
    attacker = setup.monsters[0]
    target = setup.heroes[0]

    assert has_adjacent_active_ally(attacker, setup) is False
    assert pack_tactics_active(attacker, target, setup) is False


def test_pack_tactics_advantage_is_auditable_on_attack_event() -> None:
    setup = _rat_pack_setup()
    attacker = setup.monsters[0]
    target = setup.heroes[0]
    pack = pack_tactics_active(attacker, target, setup)

    event = resolve_attack(
        1,
        1,
        attacker.state,
        target.state,
        attacker.state.template.weapon_attack,
        combatant_distance(attacker, target),
        FixedDiceProvider([5, 15, 4]),
        actor_event_id=attacker.combatant_id,
        target_event_id=target.combatant_id,
        advantage_sources=1 if pack else 0,
        feature_id="pack-tactics" if pack else None,
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.rolls == [5, 15]
    assert event.attack_roll.selected_roll == 15
    assert event.feature_id == "pack-tactics"
    assert event.hit is True

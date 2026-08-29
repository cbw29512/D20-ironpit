from app.combat.ally_context import pack_tactics_active
from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import combatant_distance
from app.domain.models import CombatTrait, EncounterSelection, RollMode


def _rat_pack_setup():
    return build_encounter_setup(EncounterSelection(
        hero_ids=["aldric-vane-l1"],
        monster_ids=["srd-giant-rat", "srd-giant-rat"],
        starting_distance_ft=5,
    ))


def test_giant_rat_is_marked_with_pack_tactics() -> None:
    setup = _rat_pack_setup()
    assert CombatTrait.PACK_TACTICS in setup.monsters[0].state.template.combat_traits


def test_pack_tactics_requires_active_ally_within_five_feet_of_target() -> None:
    setup = _rat_pack_setup()
    attacker, ally = setup.monsters
    target = setup.heroes[0]

    assert pack_tactics_active(attacker, target, setup) is True

    ally.position_ft = 15
    assert pack_tactics_active(attacker, target, setup) is False

    ally.position_ft = 5
    ally.state.current_hp = 0
    ally.state.is_unconscious = True
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

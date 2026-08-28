from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.engine import run_duel
from app.combat.masteries import apply_weapon_mastery_on_hit
from app.combat.state import build_combatant_state, expire_attack_roll_effects_at_turn_start
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.equipment import build_longsword, build_scimitar, build_shortbow
from app.domain.models import RollMode


def test_weapon_records_match_srd_masteries() -> None:
    assert build_longsword().mastery_property == "sap"
    assert build_scimitar().mastery_property == "nick"
    assert build_shortbow().mastery_property == "vex"


def test_longsword_hit_applies_sap_to_mastered_weapon() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())

    event = resolve_attack(
        1,
        1,
        fighter,
        goblin,
        fighter.template.weapon_attack,
        5,
        FixedDiceProvider([15, 4]),
    )

    assert event.hit is True
    assert event.feature_id == "sap"
    assert len(goblin.attack_roll_effects) == 1
    assert goblin.attack_roll_effects[0].id == "sap"
    assert goblin.attack_roll_effects[0].source_actor_id == fighter.template.id


def test_sap_imposes_disadvantage_on_next_attack_and_is_consumed() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    apply_weapon_mastery_on_hit(fighter, goblin, fighter.template.weapon_attack.weapon)

    event = resolve_attack(
        2,
        1,
        goblin,
        fighter,
        goblin.template.weapon_attack,
        5,
        FixedDiceProvider([18, 7]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.attack_roll.rolls == [18, 7]
    assert event.hit is False
    assert goblin.attack_roll_effects == []


def test_unused_sap_expires_at_start_of_source_turn() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    apply_weapon_mastery_on_hit(fighter, goblin, fighter.template.weapon_attack.weapon)

    expire_attack_roll_effects_at_turn_start(fighter, (fighter, goblin))

    assert goblin.attack_roll_effects == []


def test_sap_requires_mastery_of_the_weapon_kind() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    fighter.template.weapon_masteries = []

    event = resolve_attack(
        1,
        1,
        fighter,
        goblin,
        fighter.template.weapon_attack,
        5,
        FixedDiceProvider([15, 4]),
    )

    assert event.hit is True
    assert event.feature_id is None
    assert goblin.attack_roll_effects == []


def test_sap_changes_the_next_attack_in_a_full_duel() -> None:
    # Fighter wins initiative, lands Sap, Goblin then rolls 18/7 and must take 7.
    battle = run_duel(
        build_demo_fighter(),
        build_goblin_warrior(),
        FixedDiceProvider([15, 10, 14, 3, 18, 7, 12, 4]),
    )
    attacks = [event for event in battle.events if event.event_type == "attack"]

    assert attacks[0].actor_id == "aldric-vane-l1"
    assert attacks[0].feature_id == "sap"
    assert attacks[1].actor_id == "srd-goblin-warrior"
    assert attacks[1].attack_roll is not None
    assert attacks[1].attack_roll.mode is RollMode.DISADVANTAGE
    assert attacks[1].attack_roll.rolls == [18, 7]
    assert attacks[1].hit is False
    assert battle.winner_id == "aldric-vane-l1"

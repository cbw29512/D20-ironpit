from app.combat.attack_legality import attack_allowed_against
from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.domain.weapons import Weapon, WeaponAttack, WeaponAttackKind


def _tail() -> WeaponAttack:
    return WeaponAttack(
        id="tail",
        weapon=Weapon(
            id="tail",
            name="Tail",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=6,
            damage_type="bludgeoning",
            animation="melee",
            reach_ft=10,
        ),
        attack_bonus=1,
        damage_bonus=0,
        grapple_target_policy="auto_hit_own_grapple",
    )


def _state():
    return build_combatant_state(build_demo_fighter())


def test_grapple_locked_attack_only_allows_its_held_target() -> None:
    attack = _tail()
    held = _state()
    other = _state()
    apply_grapple(held, "attacker", 14, 10, source_effect_id=attack.id)

    opponents = [held, other]
    assert attack_allowed_against(attack, "attacker", held, opponents) is True
    assert attack_allowed_against(attack, "attacker", other, opponents) is False


def test_grapple_locked_attack_auto_hits_without_d20_roll() -> None:
    attack = _tail()
    attacker = _state()
    defender = _state()
    defender.template = defender.template.model_copy(update={"armor_class": 99})
    apply_grapple(defender, "attacker", 14, 10, source_effect_id=attack.id)

    event = resolve_attack(
        1,
        1,
        attacker,
        defender,
        attack,
        5,
        FixedDiceProvider([4]),
        actor_event_id="attacker",
    )

    assert event.hit is True
    assert event.attack_roll is None
    assert event.critical is False
    assert event.damage_roll is not None
    assert event.damage_roll.total == 4
    assert "Automatic hit: no attack roll." in event.description

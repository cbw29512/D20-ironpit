from app.combat.hit_points import effective_max_hp
from app.combat.max_hp_drain import resolve_max_hp_drain
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.domain.event_support import DamageRollComponent
from app.domain.max_hp_drain import MaxHpDrainEffect
from app.domain.weapons import Weapon, WeaponAttack, WeaponAttackKind


def _attack() -> WeaponAttack:
    return WeaponAttack(
        id="draining-bite",
        weapon=Weapon(
            id="draining-bite", name="Draining Bite", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=6, damage_type="piercing", animation="bite",
        ),
        attack_bonus=5, damage_bonus=2,
        max_hp_drain=MaxHpDrainEffect(damage_type="necrotic", heal_attacker=True),
    )


def _component(damage_type: str, applied: int) -> DamageRollComponent:
    return DamageRollComponent(
        source="Draining Bite", notation=str(applied), rolls=[], damage_type=damage_type,
        total=applied, applied_total=applied,
    )


def test_direct_drain_uses_only_post_defense_matching_damage_and_heals_attacker() -> None:
    attacker = build_combatant_state(build_demo_fighter())
    defender = build_combatant_state(build_demo_fighter())
    attacker.current_hp = effective_max_hp(attacker) - 10
    defender_max_before = effective_max_hp(defender)

    reduced, healed = resolve_max_hp_drain(
        attacker, defender, _attack(), [_component("piercing", 7), _component("necrotic", 4)],
    )

    assert reduced == 4 and healed == 4
    assert effective_max_hp(defender) == defender_max_before - 4
    assert attacker.current_hp == effective_max_hp(attacker) - 6


def test_direct_drain_does_nothing_when_matching_damage_is_fully_prevented() -> None:
    attacker = build_combatant_state(build_demo_fighter())
    defender = build_combatant_state(build_demo_fighter())
    before = effective_max_hp(defender)
    assert resolve_max_hp_drain(attacker, defender, _attack(), [_component("necrotic", 0)]) == (0, 0)
    assert effective_max_hp(defender) == before


def test_direct_drain_kills_when_effective_max_hp_reaches_zero() -> None:
    attacker = build_combatant_state(build_demo_fighter())
    defender = build_combatant_state(build_demo_fighter())
    defender.max_hp_reduction = effective_max_hp(defender) - 2
    defender.current_hp = 2

    reduced, _ = resolve_max_hp_drain(attacker, defender, _attack(), [_component("necrotic", 5)])

    assert reduced == 2
    assert effective_max_hp(defender) == 0
    assert defender.current_hp == 0 and defender.is_dead and not defender.is_alive

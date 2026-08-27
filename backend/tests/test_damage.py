from app.combat.attacks import resolve_attack
from app.combat.damage import calculate_applied_damage, resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.srd_monsters import build_knight, build_ogre, build_skeleton
from app.domain.models import DamageRollComponent, DamageType, RollMode


def test_goblin_normal_hit_does_not_get_advantage_bonus_damage() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    total, components = resolve_weapon_damage(
        goblin,
        goblin.template.weapon_attack,
        FixedDiceProvider([4]),
        critical=False,
        attack_mode=RollMode.NORMAL,
    )

    assert total.total == 6
    assert len(components) == 1
    assert components[0].notation == "1d6+2"


def test_goblin_advantage_hit_adds_one_d4_damage() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    total, components = resolve_weapon_damage(
        goblin,
        goblin.template.weapon_attack,
        FixedDiceProvider([4, 3]),
        critical=False,
        attack_mode=RollMode.ADVANTAGE,
    )

    assert total.total == 9
    assert [component.notation for component in components] == ["1d6+2", "1d4+0"]
    assert components[1].source == "Advantage bonus damage"


def test_goblin_advantage_critical_doubles_base_and_bonus_damage_dice() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    total, components = resolve_weapon_damage(
        goblin,
        goblin.template.weapon_attack,
        FixedDiceProvider([4, 5, 2, 3]),
        critical=True,
        attack_mode=RollMode.ADVANTAGE,
    )

    assert total.total == 16
    assert [component.notation for component in components] == ["2d6+2", "2d4+0"]


def test_longsword_has_no_goblin_advantage_bonus_damage() -> None:
    fighter = build_combatant_state(build_demo_fighter())

    total, components = resolve_weapon_damage(
        fighter,
        fighter.template.weapon_attack,
        FixedDiceProvider([7]),
        critical=False,
        attack_mode=RollMode.ADVANTAGE,
    )

    assert total.total == 10
    assert len(components) == 1
    assert components[0].source == "Longsword"


def test_ogre_attack_profile_overrides_intrinsic_greatclub_dice() -> None:
    ogre = build_combatant_state(build_ogre())

    total, components = resolve_weapon_damage(
        ogre,
        ogre.template.weapon_attack,
        FixedDiceProvider([8, 1]),
        critical=False,
        attack_mode=RollMode.NORMAL,
    )

    assert total.total == 13
    assert components[0].notation == "2d8+4"
    assert ogre.template.weapon_attack.weapon.dice_count == 1


def test_knight_radiant_rider_applies_on_normal_hit_and_critical() -> None:
    knight = build_combatant_state(build_knight())

    total, components = resolve_weapon_damage(
        knight,
        knight.template.weapon_attack,
        FixedDiceProvider([4, 5, 6]),
        critical=False,
        attack_mode=RollMode.NORMAL,
    )
    assert total.total == 18
    assert [component.notation for component in components] == ["2d6+3", "1d8+0"]
    assert components[1].damage_type is DamageType.RADIANT

    critical, crit_components = resolve_weapon_damage(
        knight,
        knight.template.weapon_attack,
        FixedDiceProvider([1, 2, 3, 4, 5, 6]),
        critical=True,
        attack_mode=RollMode.NORMAL,
    )
    assert critical.total == 21
    assert [component.notation for component in crit_components] == ["4d6+3", "2d8+0"]


def test_skeleton_bludgeoning_vulnerability_changes_applied_not_raw_damage() -> None:
    ogre = build_combatant_state(build_ogre())
    skeleton = build_combatant_state(build_skeleton())

    event = resolve_attack(
        sequence=1,
        round_number=1,
        attacker=ogre,
        defender=skeleton,
        attack=ogre.template.weapon_attack,
        distance_ft=5,
        dice=FixedDiceProvider([10, 1, 1]),
    )

    assert event.damage_roll is not None
    assert event.damage_roll.total == 6
    assert event.damage_applied == 12
    assert event.hp_before == 13
    assert event.hp_after == 1


def test_damage_immunity_and_resistance_vulnerability_order() -> None:
    skeleton = build_combatant_state(build_skeleton())
    poison = DamageRollComponent(
        source="Poison",
        notation="1d8+0",
        rolls=[8],
        damage_type=DamageType.POISON,
        total=8,
    )
    bludgeoning = DamageRollComponent(
        source="Club",
        notation="1d6+0",
        rolls=[5],
        damage_type=DamageType.BLUDGEONING,
        total=5,
    )

    assert calculate_applied_damage(skeleton, [poison]) == 0
    assert calculate_applied_damage(skeleton, [bludgeoning]) == 10

    skeleton.template.damage_resistances = [DamageType.BLUDGEONING]
    assert calculate_applied_damage(skeleton, [bludgeoning]) == 4


def test_same_type_components_are_combined_before_resistance() -> None:
    skeleton = build_combatant_state(build_skeleton())
    skeleton.template.damage_vulnerabilities = []
    skeleton.template.damage_resistances = [DamageType.BLUDGEONING]
    components = [
        DamageRollComponent(
            source="Base",
            notation="1d4+0",
            rolls=[3],
            damage_type=DamageType.BLUDGEONING,
            total=3,
        ),
        DamageRollComponent(
            source="Rider",
            notation="1d4+0",
            rolls=[3],
            damage_type=DamageType.BLUDGEONING,
            total=3,
        ),
    ]

    assert calculate_applied_damage(skeleton, components) == 3

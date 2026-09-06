from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import ConditionalDamage, DamageType, RollMode


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


def test_great_weapon_fighting_floors_each_weapon_damage_die_to_three() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    attack = fighter.template.weapon_attack.model_copy(update={"damage_die_minimum": 3})

    total, components = resolve_weapon_damage(
        fighter,
        attack,
        FixedDiceProvider([1]),
        critical=False,
        attack_mode=RollMode.NORMAL,
    )

    assert components[0].rolls == [3]
    assert total.total == 3 + attack.damage_bonus


def _replacement(trigger: str) -> ConditionalDamage:
    return ConditionalDamage(
        trigger=trigger,
        mode="replace_weapon",
        dice_count=1,
        dice_size=8,
        damage_bonus=2,
        damage_type=DamageType.SLASHING,
    )


def test_target_bloodied_replaces_weapon_damage_profile() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_fighter())
    target.current_hp = target.template.max_hp // 2
    attack = goblin.template.weapon_attack.model_copy(deep=True)
    attack.conditional_damage = [_replacement("target_bloodied")]

    total, components = resolve_weapon_damage(
        goblin, attack, FixedDiceProvider([7]), False, RollMode.NORMAL, target=target,
    )

    assert total.total == 9
    assert components[0].notation == "1d8+2"


def test_target_not_bloodied_keeps_base_weapon_damage_profile() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_fighter())
    attack = goblin.template.weapon_attack.model_copy(deep=True)
    attack.conditional_damage = [_replacement("target_bloodied")]

    total, components = resolve_weapon_damage(
        goblin, attack, FixedDiceProvider([4]), False, RollMode.NORMAL, target=target,
    )

    assert total.total == 6
    assert components[0].notation == "1d6+2"


def test_attacker_bloodied_replaces_weapon_damage_profile() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    goblin.current_hp = goblin.template.max_hp // 2
    attack = goblin.template.weapon_attack.model_copy(deep=True)
    attack.conditional_damage = [_replacement("attacker_bloodied")]

    total, components = resolve_weapon_damage(
        goblin, attack, FixedDiceProvider([5]), False, RollMode.NORMAL,
    )

    assert total.total == 7
    assert components[0].notation == "1d8+2"


def test_bloodied_replacement_critical_doubles_replacement_dice() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_fighter())
    target.current_hp = target.template.max_hp // 2
    attack = goblin.template.weapon_attack.model_copy(deep=True)
    attack.conditional_damage = [_replacement("target_bloodied")]

    total, components = resolve_weapon_damage(
        goblin, attack, FixedDiceProvider([7, 6]), True, RollMode.NORMAL, target=target,
    )

    assert total.total == 15
    assert components[0].notation == "2d8+2"


def test_target_grappled_by_same_source_replaces_weapon_damage_profile() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_fighter())
    apply_grapple(target, "attacker-1", 13, 5)
    attack = goblin.template.weapon_attack.model_copy(deep=True)
    attack.conditional_damage = [_replacement("target_grappled_by_self")]

    total, components = resolve_weapon_damage(
        goblin, attack, FixedDiceProvider([7]), False, RollMode.NORMAL,
        target=target, attacker_id="attacker-1",
    )

    assert total.total == 9
    assert components[0].notation == "1d8+2"


def test_other_creatures_grapple_does_not_trigger_self_replacement_damage() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_fighter())
    apply_grapple(target, "other-1", 13, 5)
    attack = goblin.template.weapon_attack.model_copy(deep=True)
    attack.conditional_damage = [_replacement("target_grappled_by_self")]

    total, components = resolve_weapon_damage(
        goblin, attack, FixedDiceProvider([4]), False, RollMode.ADVANTAGE,
        target=target, attacker_id="attacker-1",
    )

    assert total.total == 6
    assert components[0].notation == "1d6+2"

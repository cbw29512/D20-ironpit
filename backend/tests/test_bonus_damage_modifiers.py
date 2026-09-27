from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import add_modifier
from app.combat.spell_attack_helpers import roll_spell_attack_damage
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.models import DamageType, RollMode
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.spells import SpellAttackAction


def _state():
    return build_combatant_state(build_goblin_warrior())


def test_source_owned_bonus_damage_modifier_rolls_on_weapon_hit() -> None:
    attacker = _state()
    target = _state()
    add_modifier(attacker, CombatModifier(
        id="caster:divine-favor:self:0",
        source_id="caster",
        source_effect_id="divine-favor",
        source_name="Divine Favor",
        source_is_magical=True,
        kind=ModifierKind.BONUS_DAMAGE,
        dice_count=1,
        dice_size=4,
        damage_type=DamageType.RADIANT,
        target_id=None,
    ))

    roll, components = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([3, 4]),
        False,
        RollMode.NORMAL,
        target=target,
        target_event_id="target-1",
    )

    rider = next(item for item in components if item.source == "Divine Favor")
    assert rider.notation == "1d4+0"
    assert rider.rolls == [4]
    assert rider.damage_type is DamageType.RADIANT
    assert roll.total == sum(item.total for item in components)


def test_bonus_damage_modifier_doubles_dice_on_critical() -> None:
    attacker = _state()
    target = _state()
    add_modifier(attacker, CombatModifier(
        id="caster:divine-favor:self:0",
        source_id="caster",
        source_effect_id="divine-favor",
        source_name="Divine Favor",
        source_is_magical=True,
        kind=ModifierKind.BONUS_DAMAGE,
        dice_count=1,
        dice_size=4,
        damage_type=DamageType.RADIANT,
        target_id=None,
    ))

    _, components = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([3, 2, 4, 1]),
        True,
        RollMode.NORMAL,
        target=target,
        target_event_id="target-1",
    )

    rider = next(item for item in components if item.source == "Divine Favor")
    assert rider.notation == "2d4+0"
    assert rider.rolls == [4, 1]


def test_target_scoped_bonus_damage_only_applies_to_matching_target() -> None:
    attacker = _state()
    target = _state()
    add_modifier(attacker, CombatModifier(
        id="caster:marked-target:rider:0",
        source_id="caster",
        source_effect_id="marked-rider",
        source_name="Marked Rider",
        kind=ModifierKind.BONUS_DAMAGE,
        dice_count=1,
        dice_size=4,
        damage_type=DamageType.RADIANT,
        target_id="target-2",
    ))

    _, wrong = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([3]),
        False,
        RollMode.NORMAL,
        target=target,
        target_event_id="target-1",
    )
    assert all(item.source != "Marked Rider" for item in wrong)

    _, right = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([3, 4]),
        False,
        RollMode.NORMAL,
        target=target,
        target_event_id="target-2",
    )
    assert any(item.source == "Marked Rider" for item in right)


def test_target_scoped_bonus_damage_applies_to_spell_attack_hit() -> None:
    attacker = _state()
    add_modifier(attacker, CombatModifier(
        id="caster:marked-target:rider:spell",
        source_id="caster",
        source_effect_id="marked-rider",
        source_name="Marked Rider",
        source_is_magical=True,
        kind=ModifierKind.BONUS_DAMAGE,
        dice_count=1,
        dice_size=6,
        damage_type=DamageType.NECROTIC,
        target_id="target-1",
        concentration_required=True,
    ))
    spell = SpellAttackAction(
        id="test-blast", name="Test Blast", level=0, range_ft=120, attack_bonus=5,
        damage_dice_count=1, damage_dice_size=10, damage_type="force",
    )

    roll, components = roll_spell_attack_damage(
        spell, False, FixedDiceProvider([7, 4]),
        attacker=attacker, target_event_id="target-1",
    )

    assert [item.source for item in components] == ["Test Blast", "Marked Rider"]
    assert [item.damage_type for item in components] == [DamageType.FORCE, DamageType.NECROTIC]
    assert roll.total == 11


def test_target_scoped_bonus_damage_does_not_apply_to_other_spell_attack_target() -> None:
    attacker = _state()
    add_modifier(attacker, CombatModifier(
        id="caster:marked-target:rider:spell",
        source_id="caster", source_effect_id="marked-rider", source_name="Marked Rider",
        kind=ModifierKind.BONUS_DAMAGE, dice_count=1, dice_size=6,
        damage_type=DamageType.NECROTIC, target_id="target-2", concentration_required=True,
    ))
    spell = SpellAttackAction(
        id="test-blast", name="Test Blast", level=0, range_ft=120, attack_bonus=5,
        damage_dice_count=1, damage_dice_size=10, damage_type="force",
    )

    _, components = roll_spell_attack_damage(
        spell, False, FixedDiceProvider([7]), attacker=attacker, target_event_id="target-1",
    )

    assert [item.source for item in components] == ["Test Blast"]

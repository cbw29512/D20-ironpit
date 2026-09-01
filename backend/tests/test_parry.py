from app.combat.parry import resolve_parry_hit
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import WeaponAttackKind
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.reactions import ParryReaction


def _defender():
    state = build_combatant_state(build_demo_fighter())
    state.template.parry_reaction = ParryReaction(ac_bonus=2)
    return state


def _attack(kind: WeaponAttackKind = WeaponAttackKind.MELEE):
    attack = build_goblin_warrior().weapon_attack.model_copy(deep=True)
    attack.weapon.attack_kind = kind
    return attack


def test_parry_spends_reaction_only_when_bonus_changes_hit_to_miss() -> None:
    defender = _defender()
    total = defender.template.armor_class + 1
    hit, used = resolve_parry_hit(defender, _attack(), total, 12, True)
    assert (hit, used) == (False, True)
    assert defender.reaction_available is False


def test_parry_uses_effective_ac_before_adding_its_reaction_bonus() -> None:
    defender = _defender()
    defender.active_modifiers.append(CombatModifier(
        id="shield-ac", source_id="cleric", source_effect_id="shield-of-faith",
        kind=ModifierKind.ARMOR_CLASS, flat_bonus=2,
    ))
    total = defender.template.armor_class + 3
    hit, used = resolve_parry_hit(defender, _attack(), total, 12, True)
    assert (hit, used) == (False, True)
    assert defender.reaction_available is False


def test_parry_does_not_waste_reaction_when_boosted_ac_is_still_hit() -> None:
    defender = _defender()
    total = defender.template.armor_class + defender.template.parry_reaction.ac_bonus
    assert resolve_parry_hit(defender, _attack(), total, 12, True) == (True, False)
    assert defender.reaction_available is True


def test_parry_never_changes_ranged_hit() -> None:
    defender = _defender()
    assert resolve_parry_hit(defender, _attack(WeaponAttackKind.RANGED), defender.template.armor_class, 12, True) == (True, False)
    assert defender.reaction_available is True


def test_parry_never_changes_natural_twenty() -> None:
    defender = _defender()
    assert resolve_parry_hit(defender, _attack(), defender.template.armor_class, 20, True) == (True, False)
    assert defender.reaction_available is True


def test_parry_requires_available_reaction() -> None:
    defender = _defender()
    defender.reaction_available = False
    assert resolve_parry_hit(defender, _attack(), defender.template.armor_class, 12, True) == (True, False)

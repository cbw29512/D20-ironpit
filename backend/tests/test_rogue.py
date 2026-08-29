from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.content.pregens import build_mara_quickstep
from app.domain.models import CombatantState, RollMode


def _mara_state() -> CombatantState:
    template = build_mara_quickstep()
    return CombatantState(template=template, current_hp=template.max_hp)


def test_mara_sneak_attack_requires_advantage_in_one_on_one_arena() -> None:
    state = _mara_state()
    attack = state.template.weapon_attack

    normal, normal_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([4]), critical=False, attack_mode=RollMode.NORMAL
    )
    advantaged, advantage_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([4, 5]), critical=False, attack_mode=RollMode.ADVANTAGE
    )

    assert normal.total == 7
    assert len(normal_components) == 1
    assert advantaged.total == 12
    assert len(advantage_components) == 2
    assert advantage_components[1].rolls == [5]


def test_mara_critical_doubles_weapon_and_sneak_attack_dice() -> None:
    state = _mara_state()
    damage, components = resolve_weapon_damage(
        state,
        state.template.weapon_attack,
        FixedDiceProvider([4, 5, 6, 3]),
        critical=True,
        attack_mode=RollMode.ADVANTAGE,
    )

    assert damage.total == 21
    assert components[0].rolls == [4, 5]
    assert components[1].rolls == [6, 3]

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.content.pregens import build_mara_quickstep
from app.domain.models import CombatantState, RollMode


def _mara_state() -> CombatantState:
    template = build_mara_quickstep()
    return CombatantState(template=template, current_hp=template.max_hp)


def test_mara_sneak_attack_requires_advantage_when_no_ally_is_available() -> None:
    state = _mara_state()
    attack = state.template.weapon_attack

    normal, normal_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([4]), critical=False, attack_mode=RollMode.NORMAL,
        turn_key="1:mara",
    )
    advantaged, advantage_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([4, 5]), critical=False, attack_mode=RollMode.ADVANTAGE,
        turn_key="1:mara",
    )

    assert normal.total == 7
    assert len(normal_components) == 1
    assert advantaged.total == 12
    assert [part.source for part in advantage_components] == ["Shortsword", "Sneak Attack"]
    assert advantage_components[1].rolls == [5]


def test_mara_sneak_attack_uses_active_ally_path_without_advantage() -> None:
    state = _mara_state()
    damage, components = resolve_weapon_damage(
        state, state.template.weapon_attack, FixedDiceProvider([4, 5]),
        critical=False, attack_mode=RollMode.NORMAL, turn_key="1:mara",
        sneak_attack_ally_available=True,
    )
    assert damage.total == 12
    assert components[1].source == "Sneak Attack"


def test_disadvantage_blocks_sneak_attack_even_when_an_ally_is_available() -> None:
    state = _mara_state()
    damage, components = resolve_weapon_damage(
        state, state.template.weapon_attack, FixedDiceProvider([4]),
        critical=False, attack_mode=RollMode.DISADVANTAGE, turn_key="1:mara",
        sneak_attack_ally_available=True,
    )
    assert damage.total == 7
    assert len(components) == 1


def test_sneak_attack_is_once_per_turn_but_can_apply_again_on_another_creatures_turn() -> None:
    state = _mara_state()
    attack = state.template.weapon_attack
    first, first_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([4, 5]), False, RollMode.NORMAL,
        turn_key="1:mara", sneak_attack_ally_available=True,
    )
    second, second_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([4]), False, RollMode.NORMAL,
        turn_key="1:mara", sneak_attack_ally_available=True,
    )
    reaction, reaction_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([4, 6]), False, RollMode.NORMAL,
        turn_key="1:enemy", sneak_attack_ally_available=True,
    )
    assert first.total == 12 and len(first_components) == 2
    assert second.total == 7 and len(second_components) == 1
    assert reaction.total == 13 and len(reaction_components) == 2


def test_mara_critical_doubles_weapon_and_sneak_attack_dice() -> None:
    state = _mara_state()
    damage, components = resolve_weapon_damage(
        state,
        state.template.weapon_attack,
        FixedDiceProvider([4, 5, 6, 3]),
        critical=True,
        attack_mode=RollMode.ADVANTAGE,
        turn_key="1:mara",
    )

    assert damage.total == 21
    assert components[0].rolls == [4, 5]
    assert components[1].source == "Sneak Attack"
    assert components[1].rolls == [6, 3]


def test_sneak_attack_requires_a_marked_finesse_or_ranged_attack_profile() -> None:
    state = _mara_state()
    ineligible = state.template.weapon_attack.model_copy(update={"sneak_attack_eligible": False})
    damage, components = resolve_weapon_damage(
        state, ineligible, FixedDiceProvider([4]), False, RollMode.ADVANTAGE,
        turn_key="1:mara",
    )
    assert damage.total == 7
    assert len(components) == 1

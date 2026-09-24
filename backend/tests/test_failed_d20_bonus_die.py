from app.combat.ability_checks import resolve_ability_check_outcome
from app.combat.dice import FixedDiceProvider
from app.combat.rolls import roll_d20
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.warlock_fiend_2014_runtime import build_varek_ashenmark_2014
from app.domain.models import RollMode


def _state():
    return build_combatant_state(build_varek_ashenmark_2014(6))


def test_dark_ones_own_luck_is_generic_resource_backed_bonus_die_data() -> None:
    state = _state()
    grants = state.template.progression_features.failed_d20_bonus_die_grants
    assert len(grants) == 1
    grant = grants[0]
    assert grant.source_id == "dark-ones-own-luck"
    assert grant.source_name == "Dark One's Own Luck"
    assert grant.resource_id == "dark-ones-own-luck"
    assert grant.dice_size == 10
    assert set(grant.test_kinds) == {"ability_check", "saving_throw"}
    resource = next(item for item in state.resources if item.id == "dark-ones-own-luck")
    assert resource.current_uses == resource.max_uses == 1


def test_dark_ones_own_luck_adds_d10_to_failed_save_and_spends_resource() -> None:
    state = _state()
    roll, succeeded = resolve_saving_throw(
        state, "wisdom", 15, FixedDiceProvider([5, 6]),
    )
    assert succeeded is True
    assert roll is not None
    assert roll.total == 15
    assert roll.revisions[-1].source_effect_id == "dark-ones-own-luck"
    assert roll.revisions[-1].kind == "additive_die"
    resource = next(item for item in state.resources if item.id == "dark-ones-own-luck")
    assert resource.current_uses == 0


def test_dark_ones_own_luck_adds_d10_to_failed_ability_check() -> None:
    state = _state()
    initial = roll_d20(FixedDiceProvider([4]), 3, RollMode.NORMAL)
    revised, succeeded = resolve_ability_check_outcome(
        state, "charisma", initial, 15, FixedDiceProvider([8]),
    )
    assert succeeded is True
    assert revised.total == 15
    assert revised.revisions[-1].kind == "additive_die"
    assert revised.revisions[-1].source_effect_id == "dark-ones-own-luck"

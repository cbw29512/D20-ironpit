from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant
from app.domain.models import RollMode


def _member(cid: str, side: str, creature_type: str) -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(
        deep=True,
        update={"creature_type": creature_type},
    )
    return EncounterCombatant(
        combatant_id=cid,
        side=side,
        position_ft=0,
        state=build_combatant_state(template),
    )


def _action() -> SavingThrowAction:
    return SavingThrowAction(
        id="typed-save",
        name="Typed Save",
        save_ability="constitution",
        dc=15,
        range_ft=60,
        save_disadvantage_creature_types=["construct"],
    )


def test_declared_creature_type_imposes_save_disadvantage() -> None:
    actor = _member("actor", "heroes", "humanoid")
    target = _member("target", "monsters", "Construct")

    event = resolve_save_action(
        1, 1, actor, target, _action(), 30, FixedDiceProvider([18, 4]),
    )

    assert event.saving_throw_roll is not None
    assert event.saving_throw_roll.mode is RollMode.DISADVANTAGE
    assert event.saving_throw_roll.selected_roll == 4
    assert "Typed Save imposes Disadvantage" in event.description


def test_other_creature_type_keeps_normal_save() -> None:
    actor = _member("actor", "heroes", "humanoid")
    target = _member("target", "monsters", "humanoid")

    event = resolve_save_action(
        1, 1, actor, target, _action(), 30, FixedDiceProvider([18]),
    )

    assert event.saving_throw_roll is not None
    assert event.saving_throw_roll.mode is RollMode.NORMAL
    assert event.saving_throw_roll.selected_roll == 18

from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.saving_throws import resolve_save_action
from app.domain.models import EncounterSelection


def _setup():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=["srd-constrictor-snake"],
    ))
    return setup, setup.monsters[0], setup.heroes[0]


def test_creature_type_automatic_save_failure_skips_d20_roll() -> None:
    _, actor, target = _setup()
    action = actor.state.template.saving_throw_actions[0].model_copy(update={
        "automatic_failure_creature_types": ["Humanoid"],
        "damage_dice_count": 0,
        "damage_type": None,
        "grapple_escape_dc": None,
    })

    event = resolve_save_action(
        1,
        1,
        actor,
        target,
        action,
        5,
        FixedDiceProvider([]),
    )

    assert event.save_succeeded is False
    assert event.saving_throw_roll is None
    assert "automatically FAILS" in event.description
    assert "Humanoid" in event.description


def test_creature_type_automatic_save_failure_does_not_replace_normal_save() -> None:
    _, actor, target = _setup()
    action = actor.state.template.saving_throw_actions[0].model_copy(update={
        "automatic_failure_creature_types": ["Plant"],
        "damage_dice_count": 0,
        "damage_type": None,
        "grapple_escape_dc": None,
    })

    event = resolve_save_action(
        1,
        1,
        actor,
        target,
        action,
        5,
        FixedDiceProvider([10]),
    )

    assert event.saving_throw_roll is not None
    assert "automatically FAILS" not in event.description

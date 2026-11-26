from __future__ import annotations

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_save_capabilities_2014 import save_capabilities_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_audible_turn_conditions_2014 import (
    source_proven_audible_turn_conditions_2014,
)


def _cloaker():
    return next(card for card in load_monster_source_2014() if card.name == "Cloaker")


def test_cloaker_moan_compiles_to_shared_hearing_save_and_timed_condition() -> None:
    action, = source_proven_audible_turn_conditions_2014(_cloaker())
    assert (action.id, action.name, action.save_ability, action.dc) == (
        "moan", "Moan", "wisdom", 13,
    )
    assert action.target_scope == "all-other-creatures"
    assert action.requires_target_hearing
    assert action.excluded_target_creature_types == ["aberration"]
    assert action.area is not None
    assert (action.area.shape, action.area.radius_ft) == ("emanation", 60)
    assert action.source_effect_immunity_on_success
    rider = action.failed_save_timed_effect
    assert rider is not None
    assert (rider.effect_id, rider.duration_rounds, rider.expiry_timing) == (
        "frightened", 1, "source_turn_end",
    )


def test_moan_is_wired_without_clearing_unresolved_cloaker_obligations() -> None:
    monster = _cloaker()
    assert "moan" in {action.id for action in save_capabilities_2014(monster)}
    blockers = set(basic_blockers_2014(monster))
    assert "source:extra-action" in blockers
    assert "attack:incomplete" not in blockers
    assert "source:trait" not in blockers


def test_complete_327_card_scan_and_source_mutation_fail_closed() -> None:
    cards = load_monster_source_2014()
    assert len(cards) == 327
    applicable = [
        card.id for card in cards
        if source_proven_audible_turn_conditions_2014(card)
    ]
    assert applicable == ["cloaker"]

    original = _cloaker()
    renamed = original.model_copy(update={"id": "synthetic-moan", "name": "Synthetic Moan"})
    assert source_proven_audible_turn_conditions_2014(renamed) == (
        source_proven_audible_turn_conditions_2014(original)
    )
    varied = original.model_copy(update={
        "source_actions": original.source_actions.replace(
            "DC 13 Wisdom saving throw", "DC 14 Wisdom saving throw", 1,
        ),
    })
    varied_action, = source_proven_audible_turn_conditions_2014(varied)
    assert varied_action.dc == 14

    incompatible = original.model_copy(update={
        "source_actions": original.source_actions.replace(
            "for the next 24 hours", "until the next dawn", 1,
        ),
    })
    assert source_proven_audible_turn_conditions_2014(incompatible) == []
    assert original.source_actions == _cloaker().source_actions

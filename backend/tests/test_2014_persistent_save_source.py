"""Source binding regressions for persistent failed-save attack effects."""
from __future__ import annotations

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_persistent_effect_2014 import (
    semantic_persistent_save_names_2014,
    source_proven_persistent_save_2014,
)


def _card(card_id: str):
    return next(card for card in load_monster_source_2014() if card.id == card_id)


def _fist(card):
    return next(attack for attack in card.attacks if attack.id == "rotting-fist")


def test_all_semantic_candidates_bind_source_declared_parameters() -> None:
    cards = load_monster_source_2014()
    candidates = [card for card in cards if semantic_persistent_save_names_2014(card)]

    assert [card.id for card in candidates] == ["mummy", "mummy-lord"]
    expected = {"mummy": 12, "mummy-lord": 16}
    for card in candidates:
        proof = source_proven_persistent_save_2014(card, _fist(card))
        assert proof is not None
        assert proof.dc == expected[card.id]
        assert proof.effect_id == "mummy-rot"
        assert proof.save_ability == "constitution"
        assert proof.cannot_regain_hit_points is True
        assert proof.allowed_removal_action_ids == ["remove-curse"]
        assert proof.delayed_max_hp_reduction_delay_hours == 24
        assert (
            proof.delayed_max_hp_reduction_dice_count,
            proof.delayed_max_hp_reduction_dice_size,
        ) == (3, 6)
        assert proof.delayed_max_hp_reduction_zero_kills is True


def test_identity_is_not_a_persistent_save_dispatch_key() -> None:
    source = _card("mummy")
    renamed = source.model_copy(update={"id": "renamed-source", "name": "Renamed Source"})

    assert source_proven_persistent_save_2014(renamed, _fist(renamed)) is not None


def test_changed_timing_or_removal_text_fails_closed() -> None:
    source = _card("mummy")
    for old, new in (
        ("for every 24 hours that elapse", "at the end of each turn"),
        ("remove curse spell or other magic", "a successful saving throw"),
    ):
        changed = source.model_copy(
            update={"source_actions": source.source_actions.replace(old, new)}
        )
        assert source_proven_persistent_save_2014(changed, _fist(source)) is None


def test_completion_clears_only_attack_incomplete_blocker() -> None:
    source = _card("mummy")
    completed = source_completed_mixed_attack_2014(source, _fist(source))

    assert completed.source_complete is True
    assert completed.on_hit_save_effect["effect_id"] == "mummy-rot"
    blockers = basic_blockers_2014(source)
    assert "attack:incomplete" not in blockers
    assert "source:extra-action" in blockers

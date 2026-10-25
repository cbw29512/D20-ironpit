"""Source binding regressions for persistent failed-save attack effects."""
from __future__ import annotations

from app.content.capability_attack_compiler import compile_attack
from app.content.monster_basic_attack_effects_2014 import basic_attack_effects_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_delayed_effect_policy_2014 import (
    delayed_effect_is_arena_neutral_2014,
)
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_persistent_effect_2014 import (
    semantic_persistent_save_names_2014,
    source_proven_persistent_save_2014,
)
from app.domain.capabilities import AttackCapabilityDefinition
from app.domain.capability_effects import DiceSpec, SavePersistentEffectDefinition
from scripts.browser_on_hit_condition_serializer import serialize_on_hit_condition_save


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


def test_hour_scale_policy_keeps_source_but_omits_arena_neutral_delay() -> None:
    source = _card("mummy")
    completed = source_completed_mixed_attack_2014(source, _fist(source))
    row = completed.on_hit_save_effect

    assert row["delayed_max_hp_reduction_delay_hours"] == 24
    assert delayed_effect_is_arena_neutral_2014(24) is True
    assert delayed_effect_is_arena_neutral_2014(1) is False


def test_real_source_compiles_and_serializes_through_universal_bridge() -> None:
    source = _card("mummy")
    attack = source_completed_mixed_attack_2014(source, _fist(source))
    effects = basic_attack_effects_2014(attack)
    persistent = next(
        effect for effect in effects
        if isinstance(effect, SavePersistentEffectDefinition)
    )
    definition = AttackCapabilityDefinition(
        id=attack.id,
        name=attack.name,
        attack_kind=attack.kind,
        attack_bonus=attack.attack_bonus,
        damage=DiceSpec(
            count=attack.damage.dice_count,
            size=attack.damage.dice_size,
            bonus=attack.damage.bonus,
        ),
        damage_type=attack.damage.type,
        animation="slash",
        reach_ft=attack.reach_ft,
        effects=effects,
    )

    compiled = compile_attack(definition)
    row = serialize_on_hit_condition_save(compiled.on_hit_condition_save)

    assert persistent.dc == 12
    assert not hasattr(persistent, "delayed_max_hp_reduction_delay_hours")
    assert row["saveAbility"] == "constitution"
    assert row["dc"] == 12
    assert row["effectId"] == "mummy-rot"
    assert row["curseId"] == "mummy-rot"
    assert row["cannotRegainHitPoints"] is True
    assert row["allowedRemovalActionIds"] == ["remove-curse"]
    assert "delayedMaxHpReduction" not in row

"""Generic attack-capability proof for persistent failed-save effects."""
from __future__ import annotations

import logging

import pytest

from app.content.capability_attack_compiler import compile_attack
from app.domain.capabilities import AttackCapabilityDefinition
from app.domain.capability_effects import (
    DiceSpec,
    SaveDamageEffectDefinition,
    SavePersistentEffectDefinition,
)

logger = logging.getLogger(__name__)


def test_persistent_effect_compiles_through_generic_attack_capability() -> None:
    try:
        definition = AttackCapabilityDefinition(
            id="renamed-fist",
            name="Renamed Fist",
            attack_kind="melee",
            attack_bonus=5,
            damage=DiceSpec(count=1, size=6, bonus=2),
            damage_type="bludgeoning",
            animation="strike",
            effects=[
                SavePersistentEffectDefinition(
                    save_ability="constitution",
                    dc=16,
                    effect_id="generic-rot",
                    curse_id="generic-rot",
                    cannot_regain_hit_points=True,
                    allowed_removal_action_ids=["remove-curse"],
                )
            ],
        )
        compiled = compile_attack(definition)
        assert compiled.on_hit_condition_save is not None
        assert compiled.on_hit_condition_save.dc == 16
        assert compiled.on_hit_condition_save.effect_id == "generic-rot"
        assert compiled.on_hit_condition_save.curse_id == "generic-rot"
        assert compiled.on_hit_condition_save.condition_id is None
        assert not hasattr(
            compiled.on_hit_condition_save,
            "delayed_max_hp_reduction_delay_hours",
        )
    except Exception:
        logger.exception("Persistent-effect generic compiler regression failed.")
        raise


def test_persistent_effect_counts_as_the_single_on_hit_save_slot() -> None:
    try:
        persistent = SavePersistentEffectDefinition(
            save_ability="constitution",
            dc=12,
            effect_id="generic-rot",
        )
        damage_save = SaveDamageEffectDefinition(
            source="secondary",
            save_ability="dexterity",
            dc=12,
            dice=DiceSpec(count=1, size=6),
            damage_type="fire",
        )
        with pytest.raises(ValueError):
            AttackCapabilityDefinition(
                id="illegal-double-save",
                name="Illegal Double Save",
                attack_kind="melee",
                attack_bonus=5,
                damage=DiceSpec(count=1, size=6),
                damage_type="bludgeoning",
                animation="strike",
                effects=[persistent, damage_save],
            )
    except Exception:
        logger.exception("Persistent-effect save-slot validation regression failed.")
        raise

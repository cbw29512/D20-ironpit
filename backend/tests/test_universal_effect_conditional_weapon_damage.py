"""One universal weapon damage replacement selected by fight-local source effect."""
from __future__ import annotations

import logging

import pytest

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.capability_from_template import definition_from_template
from app.content.monster_conditional_damage_2014 import (
    conditional_damage_effect_2014, supports_conditional_damage_2014,
)
from app.content.demo import build_goblin_warrior
from app.domain.capability_effects import DamageEffectDefinition, DiceSpec
from app.domain.models import ConditionalDamage, DamageType, RollMode
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _profile():
    return ConditionalDamage(
        trigger="attacker_active_effect", required_effect_id="large-form",
        mode="replace_weapon", dice_count=2, dice_size=6,
        damage_bonus=2, damage_type=DamageType.PIERCING,
    )


def test_generic_profile_is_source_declared_and_validated():
    try:
        spec = _profile()
        assert spec.required_effect_id == "large-form"
        for bad in (
            {"trigger": "attacker_active_effect"},
            {"trigger": "attack_advantage", "required_effect_id": "large-form"},
        ):
            with pytest.raises(ValueError, match="requires exactly one"):
                ConditionalDamage(
                    **bad, dice_count=1, dice_size=6, damage_type="piercing",
                )
        row = {
            "trigger": "attacker_active_effect",
            "required_effect_id": "large-form", "mode": "replace_weapon",
            "dice_count": 2, "dice_size": 6, "damage_bonus": 2,
            "damage_type": "piercing",
        }
        assert supports_conditional_damage_2014(row)
        assert conditional_damage_effect_2014(row, "Test spear").required_effect_id == "large-form"
        assert not supports_conditional_damage_2014({**row, "required_effect_id": ""})
        with pytest.raises(ValueError, match="required combat effect"):
            DamageEffectDefinition(
                source="Test", dice=DiceSpec(count=1, size=6),
                damage_type="piercing", required_effect_id="large-form",
            )
    except Exception:
        logger.exception("Generic source effect conditional-damage validation failed")
        raise


def test_identical_attack_changes_dice_only_while_source_buff_active():
    try:
        actor = build_combatant_state(build_goblin_warrior())
        attack = actor.template.weapon_attack.model_copy(update={
            "conditional_damage": [_profile()],
        })
        before, parts = resolve_weapon_damage(
            actor, attack, FixedDiceProvider([4]), False, RollMode.NORMAL,
        )
        assert before.total == 6
        assert [c.notation for c in parts] == ["1d6+2"]
        actor.active_effect_ids.append("large-form")
        during, parts = resolve_weapon_damage(
            actor, attack, FixedDiceProvider([3, 5]), False, RollMode.NORMAL,
        )
        assert during.total == 10
        assert [c.notation for c in parts] == ["2d6+2"]
        critical, parts = resolve_weapon_damage(
            actor, attack, FixedDiceProvider([1, 2, 3, 4]), True, RollMode.NORMAL,
        )
        assert critical.total == 12
        assert [c.notation for c in parts] == ["4d6+2"]
        actor.active_effect_ids.remove("large-form")
        after, _ = resolve_weapon_damage(
            actor, attack, FixedDiceProvider([4]), False, RollMode.NORMAL,
        )
        assert after.total == before.total
        renamed = attack.model_copy(update={"id": "homebrew-dagger"})
        actor.active_effect_ids.append("large-form")
        renamed_result, _ = resolve_weapon_damage(
            actor, renamed, FixedDiceProvider([3, 5]), False, RollMode.NORMAL,
        )
        assert renamed_result.total == during.total
    except Exception:
        logger.exception("Universal active-effect weapon profile and reset failed")
        raise


def test_roundtrip_preserves_required_effect_id():
    try:
        template = build_goblin_warrior().model_copy(deep=True)
        attack = template.weapon_attack.model_copy(update={
            "conditional_damage": [_profile()],
        })
        template.weapon_attack = attack
        compiled = compile_combatant(definition_from_template(template))
        restored = compiled.weapon_attack.conditional_damage[0]
        assert restored == _profile()
        row = template_row(compiled)
        assert row["attacks"][0]["conditionalDamage"]["requiredEffectId"] == "large-form"
    except Exception:
        logger.exception("Universal source effect conditional damage export failed")
        raise

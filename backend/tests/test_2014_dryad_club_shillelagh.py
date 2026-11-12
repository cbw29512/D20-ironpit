"""The printed innate Club enchantment is a castable universal timed buff."""
from __future__ import annotations

import logging

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.damage import resolve_weapon_damage
from app.combat.modifier_flat_bonuses import attack_roll_flat_bonus
from app.combat.modifier_stack import attack_damage_source_qualifiers
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_dryad_shillelagh_2014 import (
    innate_club_shillelagh_buff_2014,
    source_innate_club_shillelagh_attacks_2014,
)
from app.domain.damage_sources import DamageSourceQualifier
from app.domain.encounters import EncounterCombatant
from app.domain.models import RollMode

logger = logging.getLogger(__name__)


def _dryad():
    try:
        return next(card for card in load_monster_source_2014() if card.id == "dryad")
    except Exception:
        logger.exception("The printed 2014 Dryad source is missing.")
        raise


def test_innate_club_shillelagh_is_not_permanently_active() -> None:
    try:
        card = _dryad()
        before = card.model_dump_json()
        spell = innate_club_shillelagh_buff_2014(card)
        assert spell is not None
        assert (spell.action_cost, spell.resource_id, spell.resource_cost) == (
            "bonus_action", "shillelagh", 1,
        )
        assert spell.duration_rounds == 10 and not spell.concentration
        transformed = source_innate_club_shillelagh_attacks_2014(card, list(card.attacks))
        assert [attack.id for attack in transformed] == ["club"]
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        assert [attack.id for attack in [
            template.weapon_attack, *template.alternate_weapon_attacks
        ] if attack is not None] == ["2014-dryad-club"]
        assert any(action.id == "shillelagh" for action in template.timed_self_buff_actions)
        assert next(resource.max_uses for resource in template.resources
                    if resource.id == "shillelagh") == 1

        weapon = template.weapon_attack
        state = build_combatant_state(template)
        caster = EncounterCombatant(
            combatant_id="dryad", side="monsters", position_ft=5, state=state,
        )
        base, _ = resolve_weapon_damage(
            state, weapon, FixedDiceProvider([3]), False, RollMode.NORMAL,
        )
        assert base.total == 3
        assert attack_roll_flat_bonus(state, weapon.weapon.id) == 0
        assert DamageSourceQualifier.MAGICAL not in attack_damage_source_qualifiers(state, weapon)

        event = resolve_timed_self_buff(1, 1, caster, spell, spend_action_cost=True)
        assert event.feature_id == "shillelagh"
        assert state.action_available and not state.bonus_action_available
        assert attack_roll_flat_bonus(state, weapon.weapon.id) == 4
        assert DamageSourceQualifier.MAGICAL in attack_damage_source_qualifiers(state, weapon)
        enchanted, notation = resolve_weapon_damage(
            state, weapon, FixedDiceProvider([3]), False, RollMode.NORMAL,
        )
        assert enchanted.total == 7 and notation[0].notation == "1d8+4"

        active = next(effect for effect in state.timed_effects
                      if effect.source_effect_id == "shillelagh")
        assert remove_effect_group(state, active) == ["shillelagh"]
        assert attack_roll_flat_bonus(state, weapon.weapon.id) == 0
        assert DamageSourceQualifier.MAGICAL not in attack_damage_source_qualifiers(state, weapon)
        restored, _ = resolve_weapon_damage(
            state, weapon, FixedDiceProvider([3]), False, RollMode.NORMAL,
        )
        assert restored.total == base.total
        assert card.model_dump_json() == before
    except Exception:
        logger.exception("Dryad's source-bound ordinary weapon enchantment regressed.")
        raise


def test_innate_club_shillelagh_is_source_driven_and_fails_closed() -> None:
    try:
        card = _dryad()
        renamed = card.model_copy(update={"id": "renamed-fey", "name": "Renamed Fey"})
        spell = innate_club_shillelagh_buff_2014(renamed)
        assert spell is not None
        assert spell.modifier_effects[0].weapon_id == "2014-renamed-fey-club"
        changed = card.model_copy(deep=True)
        for item in changed.innate_spellcasting["spells"]:
            if item["id"] == "shillelagh":
                item["uses_per_day"] = 2
        with pytest.raises(ValueError, match="Innate Shillelagh"):
            innate_club_shillelagh_buff_2014(changed)
        assert innate_club_shillelagh_buff_2014(card) is not None
    except Exception:
        logger.exception("Dryad's printed innate spell frequency was not validated.")
        raise

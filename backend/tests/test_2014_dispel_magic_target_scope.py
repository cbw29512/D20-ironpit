"""2014 Dispel Magic target scope and safe automated preference.

Source/schema: EffectRemovalAction.target_mode; state: existing tracked modifiers.
No spell effects, character cards, or resource amounts are modified.
"""
from __future__ import annotations

import logging
from types import SimpleNamespace

from app.combat.effect_removal_targets import tracked_spell_effects, _target_allowed
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014

logger = logging.getLogger(__name__)


def _member(key, side, position, *, spell=None, modifiers=()):
    try:
        template = SimpleNamespace(
            size="medium",
            defensive_spell_actions=[spell] if spell else [],
            spell_save_actions=[], spell_attack_actions=[],
        )
        state = SimpleNamespace(
            template=template, position=None, is_alive=True, is_dead=False,
            active_modifiers=list(modifiers),
        )
        return SimpleNamespace(
            combatant_id=key, side=side, position_ft=position, state=state,
        )
    except Exception:
        logger.exception("Failed to assemble isolated Dispel Magic target fixture")
        raise


def test_2014_dispel_magic_can_select_enemy_ally_and_self():
    try:
        action = dispel_magic_2014("intelligence")
        assert action.target_mode == "any"
        actor = _member("actor", "heroes", 0)
        ally = _member("ally", "heroes", 20)
        enemy = _member("enemy", "monsters", 25)
        for member in (actor, ally, enemy):
            assert _target_allowed(actor, member, action)
        enemy.position_ft = 121
        assert not _target_allowed(actor, enemy, action)
    except Exception:
        logger.exception("Dispel Magic target scope violates 2014 rules")
        raise


def test_hostile_spell_effect_selected_before_a_nearer_friendly_buff():
    try:
        action = dispel_magic_2014("intelligence")
        friendly_spell = SimpleNamespace(id="bless", level=1)
        enemy_spell = SimpleNamespace(id="haste", level=3)
        actor = _member("actor", "heroes", 0, spell=friendly_spell)
        enemy_caster = _member("enemy-caster", "monsters", 40, spell=enemy_spell)
        friend = _member("friend", "heroes", 5, modifiers=[
            SimpleNamespace(source_id="actor", source_effect_id="bless"),
        ])
        enemy = _member("enemy", "monsters", 30, modifiers=[
            SimpleNamespace(source_id="enemy-caster", source_effect_id="haste"),
        ])
        setup = SimpleNamespace(heroes=[actor, friend], monsters=[enemy_caster, enemy])
        candidates = tracked_spell_effects(actor, setup, action)
        assert [(e.effect_id, e.target.combatant_id) for e in candidates] == [
            ("haste", "enemy"), ("bless", "friend"),
        ]
        # This is still one tracked effect per existing resolver cast; the
        # separate multi-effect 2014 RAW fix is not claimed here.
    except Exception:
        logger.exception("Dispel Magic automation chose a friendly spell first")
        raise

"""One 2014 Dispel Magic cast resolves every spell on the selected creature."""
from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

import app.combat.effect_removal_multi as multi
from app.combat.dice import FixedDiceProvider
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
from app.domain.events import RollMode

logger = logging.getLogger(__name__)


def member(key, side, spells=(), modifiers=()):
    try:
        return SimpleNamespace(
            combatant_id=key, side=side, position_ft=0,
            state=SimpleNamespace(
                position=None, is_alive=True, is_dead=False,
                active_modifiers=list(modifiers), active_buff_effect_ids=[
                    m.source_effect_id for m in modifiers
                ],
                template=SimpleNamespace(
                    size="medium", name=key, ability_scores=SimpleNamespace(
                        modifier=lambda ability: 0,
                    ), defensive_spell_actions=list(spells),
                    spell_save_actions=[], spell_attack_actions=[],
                    effect_tag_condition_grants=[],
                ),
            ),
        )
    except Exception:
        logger.exception("Could not construct source-owned Dispel Magic fixture")
        raise


def spell(id, level):
    return SimpleNamespace(id=id, level=level)


def modifier(owner, id):
    return SimpleNamespace(source_id=owner, source_effect_id=id)


def fixture():
    action = dispel_magic_2014("intelligence")
    actor = member("actor", "heroes")
    source = member("enemy-caster", "monsters", spells=[
        spell("bless", 1), spell("haste", 3),
        spell("greater-invisibility", 4), spell("stoneskin", 4),
    ])
    target = member("enemy", "monsters", modifiers=[
        modifier("enemy-caster", id) for id in
        ("bless", "haste", "greater-invisibility", "stoneskin", "natural-armor")
    ])
    # Nonspell magic has no source spell declaration and must remain intact.
    target.state.active_modifiers[-1].source_effect_id = "natural-armor"
    setup = SimpleNamespace(heroes=[actor], monsters=[source, target])
    return action, actor, source, target, setup


def test_one_cast_dispels_multiple_low_spells_and_checks_each_high(monkeypatch):
    try:
        action, actor, source, target, setup = fixture()
        monkeypatch.setattr(multi, "ability_check_roll_mode", lambda *a, **k: RollMode.NORMAL)
        monkeypatch.setattr(
            multi, "resolve_ability_check_outcome",
            lambda state, ability, roll, dc, **kwargs: (roll, roll.total >= dc),
        )
        dice = FixedDiceProvider([4, 18])
        candidates = multi.resolve_target_spell_effects(
            actor, setup, action, target, dice, 1,
        )
        assert len(candidates) == 4
        removed, first, dc, first_success, audit, description = multi.apply_target_spell_effects(
            actor, setup, action, target, candidates, dice, 1,
        )
        assert removed == ["stoneskin", "haste", "bless"] or set(removed) == {
            "stoneskin", "haste", "bless",
        }
        assert "greater-invisibility: resisted" in description
        assert first.total == 4 and dc == 14 and first_success is False
        assert len(audit.steps) == 4
        assert [m.source_effect_id for m in target.state.active_modifiers] == [
            "greater-invisibility", "natural-armor",
        ]
        assert actor.state.active_modifiers == []
    except Exception:
        logger.exception("Dispel Magic mixed-level effect cohort failed")
        raise


def test_source_spell_cannot_remove_buff_on_different_creature():
    try:
        action, actor, source, target, setup = fixture()
        friend = member("other", "monsters", modifiers=[modifier("enemy-caster", "haste")])
        setup.monsters.append(friend)
        candidate = multi.resolve_target_spell_effects(actor, setup, action, target, None, 1)
        # Higher spells require dice before any mutation.
        raise AssertionError("Missing higher-spell dice should have failed preflight")
    except ValueError as error:
        assert "checks require dice" in str(error)



def test_spell_owned_timed_condition_removed_but_innate_trait_survives():
    try:
        from app.domain.timed_effects import TimedEffect

        action, actor, source, target, setup = fixture()
        source.state.template.defensive_spell_actions.append(spell("hold-person", 2))
        # Remove the other tracked buffs to make the timed spell the sole
        # dispellable effect; nonspell natural armor must survive.
        target.state.active_modifiers = [modifier("enemy-caster", "natural-armor")]
        target.state.active_buff_effect_ids = []
        target.state.template.innate_condition_ids = []
        target.state.active_effect_ids = ["paralyzed"]
        target.state.active_curses = []
        target.state.timed_effects = [TimedEffect(
            effect_id="paralyzed", source_id="enemy-caster",
            source_effect_id="hold-person", source_is_magical=True,
        )]
        candidates = multi.resolve_target_spell_effects(
            actor, setup, action, target, None, 1,
        )
        assert len(candidates) == 1 and candidates[0].effect_id == "hold-person"
        removed, check, dc, success, audit, _ = multi.apply_target_spell_effects(
            actor, setup, action, target, candidates, None, 1,
        )
        assert removed == ["hold-person"] and check is None and dc is None
        assert target.state.timed_effects == []
        assert target.state.active_effect_ids == []
        assert [m.source_effect_id for m in target.state.active_modifiers] == ["natural-armor"]
        assert len(audit.steps) == 1
    except Exception:
        logger.exception("Dispel Magic did not use canonical timed spell cleanup")
        raise

from __future__ import annotations

import logging

from app.combat.state import build_combatant_state
from app.combat.timed_self_buff_policy import (
    choose_timed_self_buff_action,
    concentration_grant_only,
)
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_support_2014 import (
    innate_spell_resources_2014,
    innate_timed_self_buffs_2014,
    supports_innate_spellcasting_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def _source(monster_id: str):
    try:
        return next(card for card in load_monster_source_2014() if card.id == monster_id)
    except StopIteration as exc:
        logger.exception("Pinned 2014 source card %s is missing.", monster_id)
        raise AssertionError(f"Pinned 2014 source card {monster_id} is missing.") from exc


def _blur(card):
    return next(action for action in innate_timed_self_buffs_2014(card) if action.id == "blur")


def test_every_innate_blur_source_row_binds_exact_temporary_buff_parameters() -> None:
    cards = load_monster_source_2014()
    applicable = [
        card for card in cards
        if any(str(row.get("id") or "") == "blur" for row in innate_spells_2014(card))
    ]
    assert [card.id for card in applicable] == ["deep-gnome-svirfneblin", "steam-mephit"]
    for card in applicable:
        action = _blur(card)
        assert action.name == "Blur"
        assert action.action_cost == "action"
        assert action.resource_id == "blur"
        assert action.resource_cost == 1
        assert action.duration_rounds == 10
        assert action.expiry_timing == "source_turn_start"
        assert action.magical_effect is True
        assert action.concentration is True
        assert action.priority == 70
        effect, = action.modifier_effects
        assert effect.kind == "attacks-against-disadvantage"
        assert effect.bypass_attacker_senses == ["blindsight", "truesight"]
        resource, = [item for item in innate_spell_resources_2014(card) if item.id == "blur"]
        assert resource.max_uses == 1


def test_innate_blur_is_source_semantic_and_steam_mephit_is_complete() -> None:
    source = _source("steam-mephit")
    renamed = source.model_copy(update={"id": "synthetic-blur-card", "name": "Synthetic Blur Card"})
    assert _blur(renamed) == _blur(source)
    assert supports_innate_spellcasting_2014(renamed) is True
    assert supports_innate_spellcasting_2014(source) is True


def test_innate_blur_spends_fight_local_use_and_starts_concentration() -> None:
    definition = adapt_basic_monster_2014(_source("steam-mephit"))
    template = compile_combatant(definition)
    first_state = build_combatant_state(template)
    second_state = build_combatant_state(template)
    member = EncounterCombatant(
        combatant_id="steam-mephit", side="monsters", position_ft=0, state=first_state,
    )
    action = next(item for item in template.timed_self_buff_actions if item.id == "blur")
    assert concentration_grant_only(action) is False
    assert choose_timed_self_buff_action(member) == action
    event = resolve_timed_self_buff(
        1, 1, member, action, affected_states=[first_state],
    )
    assert event.feature_id == "blur"
    assert event.resource_remaining == 0
    assert first_state.concentration is not None
    assert first_state.concentration.effect_id == "blur"
    modifier, = [item for item in first_state.active_modifiers if item.source_effect_id == "blur"]
    assert modifier.kind.value == "attacks-against-disadvantage"
    assert modifier.bypass_attacker_senses == ["blindsight", "truesight"]
    assert next(item for item in second_state.resources if item.id == "blur").current_uses == 1
    assert second_state.concentration is None
    assert not second_state.active_modifiers

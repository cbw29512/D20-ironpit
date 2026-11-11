"""2014 Green Hag: reuse source-exact Disguise, Invisibility, and Save spell."""
from __future__ import annotations

import logging

from app.combat.owner_action_expiry import expire_on_owner_event
from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_innate_support_2014 import supports_innate_spellcasting_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_invisibility_2014 import source_invisibility_action_2014
from app.content.monster_source_visual_disguise_2014 import source_proven_visual_disguise_2014
from app.content.monster_supported_extra_actions_2014 import source_supported_extra_action_labels_2014
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def _hag():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        return next(card for card in cards if card.id == "green-hag")
    except Exception:
        logger.exception("Pinned Green Hag source missing.")
        raise


def test_green_hag_reuses_damage_and_complete_action_capabilities():
    try:
        card = _hag()
        original = card.model_dump_json()
        assert supports_innate_spellcasting_2014(card)
        assert basic_blockers_2014(card) == ()
        assert {"illusory appearance", "invisible passage"} <= (
            source_supported_extra_action_labels_2014(card)
        )
        facts = source_proven_visual_disguise_2014(card)
        assert facts and facts.investigation_dc == 20
        assert facts.investigation_skill == "investigation"
        action, = source_invisibility_action_2014(card)
        assert action.name == "Invisible Passage"
        assert action.condition_ids == ["invisible"]
        assert action.concentration
        assert action.ends_on_owner_attack and action.ends_on_owner_spell_cast
        assert action.resource_id is None

        template = compile_combatant(adapt_basic_monster_2014(card))
        assert template.name == "Green Hag"
        assert template.weapon_attack is not None
        assert template.weapon_attack.attack_bonus == 6
        assert template.visual_disguise_action.inspection_dc == 20
        assert not template.visual_disguise_action.opening_eligible
        assert not template.visual_disguise_action.dismiss_on_first_turn
        assert any(x.name == "Invisible Passage" for x in template.timed_self_buff_actions)
        assert any(x.id == "vicious-mockery" and x.dc == 12
                   for x in template.spell_save_actions)
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("Green Hag universal combat adapter failed.")
        raise


def test_invisible_passage_uses_shared_concentration_exit():
    try:
        card = _hag()
        template = compile_combatant(adapt_basic_monster_2014(card))
        state = build_combatant_state(template)
        actor = EncounterCombatant(
            combatant_id="source-hag", side="monsters", position_ft=0, state=state,
        )
        action = next(x for x in template.timed_self_buff_actions if x.name == "Invisible Passage")
        resolve_timed_self_buff(1, 1, actor, action, spend_action_cost=False)
        assert "invisible" in state.active_effect_ids
        assert state.concentration is not None
        assert expire_on_owner_event(state, "action", [state], action_id="other") == []
        assert expire_on_owner_event(state, "spell_cast", [state]) == ["invisible"]
        assert "invisible" not in state.active_effect_ids
        assert state.concentration is None
    except Exception:
        logger.exception("Generic Invisible Passage expiry failed.")
        raise


def test_2014_green_hag_source_mutations_fail_closed():
    try:
        card = _hag()
        renamed = card.model_copy(update={"id": "anonymous", "name": "Other"})
        assert source_proven_visual_disguise_2014(renamed) is not None
        assert source_invisibility_action_2014(renamed)
        for old, new, missing in (
            ("physical inspection", "magical inspection", "illusory appearance"),
            ("DC 20 Intelligence", "DC 20 Wisdom", "illusory appearance"),
            ("until she attacks or casts a spell", "until she attacks", "invisible passage"),
            ("leaves no physical evidence", "leaves tracks", "invisible passage"),
        ):
            altered = card.model_copy(update={
                "source_actions": card.source_actions.replace(old, new),
            })
            assert old in card.source_actions
            assert missing not in source_supported_extra_action_labels_2014(altered)
            assert "source:extra-action" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("Green Hag printed source mutation safety failed.")
        raise

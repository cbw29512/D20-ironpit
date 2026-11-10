"""Source-named 2014 Duergar actions compose through universal owner expiry."""
from __future__ import annotations

import logging

import pytest

from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def test_duergar_invisibility_ends_on_real_enlarge_and_both_resources_spend():
    try:
        source = next(card for card in load_monster_source_2014() if card.id == "duergar")
        template = compile_combatant(adapt_monster_mechanics_2014(source))
        state = build_combatant_state(template)
        member = EncounterCombatant(
            combatant_id="duergar-unit", side="monsters", position_ft=0,
            state=state,
        )
        actions = {action.id: action for action in template.timed_self_buff_actions}
        assert {"invisibility", "enlarge"} <= set(actions)
        resources = {item.id: item for item in state.resources}
        assert resources["invisibility"].current_uses == 1
        assert resources["enlarge"].current_uses == 1

        unseen = resolve_timed_self_buff(
            1, 1, member, actions["invisibility"], spend_action_cost=False,
        )
        assert unseen.description.endswith("uses Invisibility.")
        assert state.concentration is not None
        assert "invisible" in state.active_effect_ids
        assert resources["invisibility"].current_uses == 0

        grown = resolve_timed_self_buff(
            2, 2, member, actions["enlarge"], spend_action_cost=False,
        )
        assert grown.description.endswith("uses Enlarge.")
        assert state.concentration is None
        assert "invisible" not in state.active_effect_ids
        assert "enlarge" in state.active_effect_ids
        assert state.template.size.value == "large"
        assert resources["enlarge"].current_uses == 0
        assert resources["invisibility"].current_uses == 0

        with pytest.raises(ValueError, match="Resource"):
            resolve_timed_self_buff(
                3, 3, member, actions["enlarge"], spend_action_cost=False,
            )
    except Exception:
        logger.exception("Printed Duergar action composition broke the shared engine")
        raise

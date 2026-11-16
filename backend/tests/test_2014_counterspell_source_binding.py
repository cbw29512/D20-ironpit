"""2014 Counterspell source -> immutable definition -> browser reaction parity."""
from __future__ import annotations

import logging

from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_counterspell_source_2014 import (
    source_counterspell_reactions_2014,
    source_proves_prepared_counterspell_2014,
)
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def test_all_proven_prepared_counterspell_casters_have_shared_reaction():
    try:
        casters = [
            monster for monster in load_monster_source_2014()
            if source_proves_prepared_counterspell_2014(monster)
        ]
        assert len(casters) >= 3
        for monster in casters:
            original = monster.model_dump_json()
            reaction = source_counterspell_reactions_2014(monster)
            assert len(reaction) == 1
            action = reaction[0]
            assert action.name == "Counterspell"
            assert action.printed_level == 3 and action.range_ft == 60
            assert action.casting_ability == monster.spellcasting["ability"]
            assert monster.model_dump_json() == original
    except Exception:
        logger.exception("Counterspell source binding cohort failed")
        raise


def test_prepared_counterspell_compiles_and_serializes_without_casting():
    try:
        monster = next(m for m in load_monster_source_2014() if m.name == "Mage")
        definition = adapt_monster_mechanics_2014(monster)
        assert len(definition.spell_interrupt_reactions) == 1
        template = compile_combatant(definition)
        row = template_row(template)
        action = row["spell_interrupt_reactions"][0]
        assert action == {
            "id": "counterspell", "name": "Counterspell",
            "printedLevel": 3, "trigger": "visible_spell_cast",
            "range": 60, "castingAbility": "intelligence",
            "resourcePrefix": "spell-slot-", "allowsHigherSlots": True,
        }
        state = build_combatant_state(template)
        assert state.reaction_available
        assert any(resource.id == "spell-slot-3" and resource.current_uses > 0
                   for resource in state.resources)
        assert all(x.id != "counterspell" for x in template.spell_save_actions)
    except Exception:
        logger.exception("Prepared Counterspell schema/serialization parity failed")
        raise


def test_malformed_casting_ability_never_grants_reaction():
    try:
        monster = next(m for m in load_monster_source_2014() if m.name == "Mage")
        changed = monster.model_copy(update={
            "spellcasting": {**monster.spellcasting, "ability": "wisdom"},
        })
        assert source_proves_prepared_counterspell_2014(changed)
        assert source_counterspell_reactions_2014(changed) == []
        commoner = next(m for m in load_monster_source_2014() if m.name == "Commoner")
        assert source_counterspell_reactions_2014(commoner) == []
    except Exception:
        logger.exception("Counterspell source ability mutation accepted")
        raise

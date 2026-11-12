"""2014 Cloud Giant Misty Step reuses the shared in-place teleport escape."""
from __future__ import annotations

import logging

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_innate_misty_step_2014 import source_proven_innate_misty_step_2014
from app.content.monster_innate_support_2014 import (
    innate_spell_resources_2014,
    supports_innate_spellcasting_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import _teleport

logger = logging.getLogger(__name__)


def _cloud_giant():
    try:
        monsters = load_monster_source_2014()
        assert len(monsters) == 327
        return next(item for item in monsters if item.id == "cloud-giant")
    except Exception:
        logger.exception("2014 Cloud Giant source record unavailable.")
        raise


def test_cloud_giant_misty_step_binds_to_shared_in_place_escape():
    try:
        source = _cloud_giant()
        snapshot = source.model_dump_json()
        (action,) = source_proven_innate_misty_step_2014(source)

        assert (action.id, action.name, action.level) == (
            "misty-step", "Misty Step", 2,
        )
        assert action.action_cost == "bonus_action"
        assert action.range_ft == 30
        assert action.resource_id == "misty-step"
        assert action.resource_cost == 1
        assert not action.expends_spell_slot

        # The exact printed 3/day frequency becomes the fight-local resource.
        resources = {row.id: row.max_uses for row in innate_spell_resources_2014(source)}
        assert resources["misty-step"] == 3

        template = compile_combatant(adapt_monster_mechanics_2014(source))
        assert template.teleport_actions == [action]
        assert {row.id: row.max_uses for row in template.resources}["misty-step"] == 3

        browser = _teleport(template.teleport_actions[0])
        assert browser["actionCost"] == "bonus_action"
        assert browser["range"] == 30
        assert browser["resourceId"] == "misty-step"
        assert browser["resourceCost"] == 1
        assert not browser["expendsSpellSlot"]

        # The teleport spell is now bound, but Cloud Giant remains blocked
        # until its other printed innate spells are individually resolved.
        assert not supports_innate_spellcasting_2014(source)
        assert source.model_dump_json() == snapshot
    except Exception:
        logger.exception("Cloud Giant Misty Step binding failed.")
        raise


def test_misty_step_proof_is_source_bound_and_fails_closed():
    try:
        source = _cloud_giant()
        (action,) = source_proven_innate_misty_step_2014(source)
        renamed = source.model_copy(update={"id": "renamed-caster", "name": "Renamed"})
        assert source_proven_innate_misty_step_2014(renamed) == [action]

        changed_text = source.model_copy(update={
            "source_traits": source.source_traits.replace("misty step", "fireball"),
        })
        assert source_proven_innate_misty_step_2014(changed_text) == []

        changed_uses = source.model_copy(deep=True)
        row = next(item for item in changed_uses.innate_spellcasting["spells"]
                   if item["id"] == "misty-step")
        row["uses_per_day"] = 2
        assert source_proven_innate_misty_step_2014(changed_uses) == []
    except Exception:
        logger.exception("Cloud Giant Misty Step source-mutation proof failed.")
        raise

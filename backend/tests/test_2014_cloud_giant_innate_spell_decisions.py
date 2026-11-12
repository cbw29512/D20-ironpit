"""Cloud Giant innate spell source, arena disposition, and AI selection audit."""
from __future__ import annotations

import logging

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_environmental_spell_proofs_2014 import (
    source_proven_arena_inert_innate_spells_2014,
)
from app.content.monster_innate_ai_exclusions_2014 import (
    source_proven_arena_ai_excluded_innate_spells_2014,
)
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_support_2014 import (
    innate_spell_resources_2014,
    innate_timed_self_buffs_2014,
    supports_innate_spellcasting_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _cloud_giant():
    try:
        return next(m for m in load_monster_source_2014() if m.id == "cloud-giant")
    except Exception:
        logger.exception("Could not load pinned 2014 Cloud Giant source.")
        raise


def test_cloud_giant_innate_spell_list_is_fully_disposed_without_source_mutation():
    try:
        source = _cloud_giant()
        snapshot = source.model_dump_json()
        rows = {row["id"]: row for row in innate_spells_2014(source)}

        # Preserve the printed spell names/frequencies on the source card.
        assert rows["feather-fall"]["uses_per_day"] == 3
        assert rows["fly"]["uses_per_day"] == 3
        assert rows["misty-step"]["uses_per_day"] == 3
        assert rows["telekinesis"]["uses_per_day"] == 3
        assert rows["control-weather"]["uses_per_day"] == 1
        assert rows["gaseous-form"]["uses_per_day"] == 1

        assert source_proven_arena_inert_innate_spells_2014(source) == {
            "light", "feather-fall", "control-weather",
        }
        assert source_proven_arena_ai_excluded_innate_spells_2014(source) == {
            "fly", "telekinesis", "gaseous-form",
        }
        assert supports_innate_spellcasting_2014(source)

        # Fly stays a universal buff for other casters, but this source-owned
        # arena choice omits it from Cloud Giant's selectable combat Actions.
        assert all(action.id != "fly" for action in innate_timed_self_buffs_2014(source))
        template = compile_combatant(adapt_monster_mechanics_2014(source))
        assert [action.id for action in template.teleport_actions] == ["misty-step"]
        assert [action.id for action in template.suppression_zone_actions] == ["fog-cloud"]
        assert all(action.id != "fly" for action in template.timed_self_buff_actions)
        assert {resource.id for resource in innate_spell_resources_2014(source)} == {"misty-step"}
        assert not ({"mechanic:spellcasting", "source:trait"} & set(basic_blockers_2014(source)))

        # Browser receives the same compiled omission and the same source-owned
        # Misty Step/Fog Cloud actions; source spell metadata remains untouched.
        browser = template_row(template)
        assert [item["id"] for item in browser["teleport_actions"]] == ["misty-step"]
        assert [item["id"] for item in browser["suppression_zone_actions"]] == ["fog-cloud"]
        assert all(item["id"] != "fly" for item in browser.get("timed_self_buff_actions", []))
        assert browser["resources"]["misty-step"] == 3
        assert source.model_dump_json() == snapshot
    except Exception:
        logger.exception("Cloud Giant 2014 innate spell disposition failed.")
        raise


def test_cloud_giant_spell_exclusions_fail_closed_on_source_or_use_drift():
    try:
        source = _cloud_giant()
        changed_text = source.model_copy(update={
            "source_traits": source.source_traits.replace("telekinesis", "fireball"),
        })
        assert source_proven_arena_ai_excluded_innate_spells_2014(changed_text) == frozenset()
        assert source_proven_arena_inert_innate_spells_2014(changed_text) == frozenset()
        assert not supports_innate_spellcasting_2014(changed_text)

        changed_uses = source.model_copy(deep=True)
        row = next(item for item in changed_uses.innate_spellcasting["spells"]
                   if item["id"] == "gaseous-form")
        row["uses_per_day"] = 2
        assert source_proven_arena_ai_excluded_innate_spells_2014(changed_uses) == frozenset()
        assert not supports_innate_spellcasting_2014(changed_uses)
    except Exception:
        logger.exception("Cloud Giant 2014 innate spell source mutation guard failed.")
        raise

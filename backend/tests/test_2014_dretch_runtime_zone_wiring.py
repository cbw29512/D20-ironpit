from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014


def test_source_proven_dretch_zone_survives_capability_compilation() -> None:
    source = next(m for m in load_monster_source_2014() if m.id == "dretch")
    # Source-approved action is now bound to the universal save-zone runtime.
    from app.content.monster_basic_candidates_2014 import basic_blockers_2014
    assert basic_blockers_2014(source) == ()
    definition = adapt_basic_monster_2014(source)
    template = compile_combatant(definition)
    assert len(template.persistent_save_zone_actions) == 1
    zone = template.persistent_save_zone_actions[0]
    assert zone.id == "fetid-cloud"
    assert zone.save_context == "nonmagical"
    assert zone.target_policy == "all"
    assert zone.failed_save_action_bonus_exclusive
    assert zone.failed_save_suppress_reactions
    assert any(resource.id == "fetid-cloud" and resource.max_uses == 1 for resource in template.resources)

"""Universal Iron Pit resource lifecycle: printed rest/day labels never persist across fights."""
from __future__ import annotations

from app.combat.state import build_combatant_state
from app.combat.resources import spend_resource
from app.content.monster_fetid_cloud_2014 import fetid_cloud_zone_2014, fetid_cloud_resources_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.combatants import CombatantTemplate


def test_printed_one_day_monster_ability_refills_between_fights() -> None:
    monster = next(m for m in load_monster_source_2014() if m.id == "dretch")
    zone = fetid_cloud_zone_2014(monster)
    assert zone is not None
    # Immutable source resource definition is reused for each fresh fight.
    resource = fetid_cloud_resources_2014(monster)[0]
    assert zone.resource_id == resource.id and resource.max_uses == 1

    # Use a minimal existing production combat template, replacing only
    # its resource definitions; the state constructor is the subject here.
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
    from unittest.mock import patch
    with patch("app.content.monster_definition_adapter_2014.basic_blockers_2014", return_value=()):
        definition = adapt_basic_monster_2014(monster)
    from app.content.capability_compiler import compile_combatant
    template: CombatantTemplate = compile_combatant(definition)

    fight_one = build_combatant_state(template)
    assert next(r for r in fight_one.resources if r.id == resource.id).current_uses == 1
    assert spend_resource(fight_one, resource.id) == 0
    assert next(r for r in fight_one.resources if r.id == resource.id).current_uses == 0
    assert not any(r.id == resource.id and r.max_uses != 1 for r in template.resources)

    fight_two = build_combatant_state(template)
    assert next(r for r in fight_two.resources if r.id == resource.id).current_uses == 1
    assert fight_one.resources is not fight_two.resources
    assert fight_one.template is template and fight_two.template is template

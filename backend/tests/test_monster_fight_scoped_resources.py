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

    # A certified combat template supplies all mandatory combat fields;
    # replace its resource definitions only, without mutating the template.
    from app.content.roster import build_arena_roster
    existing = build_arena_roster("2014").monsters[0]
    template: CombatantTemplate = existing.model_copy(update={"resources": [resource]})

    fight_one = build_combatant_state(template)
    assert next(r for r in fight_one.resources if r.id == resource.id).current_uses == 1
    assert spend_resource(fight_one, resource.id) == 0
    assert next(r for r in fight_one.resources if r.id == resource.id).current_uses == 0
    assert not any(r.id == resource.id and r.max_uses != 1 for r in template.resources)

    fight_two = build_combatant_state(template)
    assert next(r for r in fight_two.resources if r.id == resource.id).current_uses == 1
    assert fight_one.resources is not fight_two.resources
    assert fight_one.template is template and fight_two.template is template


def test_every_certified_monster_resource_is_fight_scoped_in_both_editions() -> None:
    from app.content.roster import build_arena_roster

    for edition in ("2014", "2024"):
        templates = build_arena_roster(edition).monsters
        assert templates, f"No certified monsters in {edition}"
        for template in templates:
            # All resources are initialized from immutable definitions,
            # including monster-specific printed daily/rest ability uses.
            first = build_combatant_state(template)
            for resource in first.resources:
                assert resource.current_uses == resource.max_uses
                if resource.max_uses:
                    assert spend_resource(first, resource.id) == resource.max_uses - 1
            second = build_combatant_state(template)
            assert [(r.id, r.current_uses) for r in second.resources] == [
                (definition.id, definition.max_uses) for definition in template.resources
            ]
            assert first.resources is not second.resources

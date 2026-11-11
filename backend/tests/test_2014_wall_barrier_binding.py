"""2014 Wall of Ice uses universal persistent barrier card schema, not name dispatch."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_barrier_bindings_2014 import source_barrier_actions_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.capability_compiler import compile_combatant
from scripts.browser_template_serializer import persistent_barrier_row

logger = logging.getLogger(__name__)


def test_2014_source_barrier_compiles_with_real_recharge_resource_but_is_still_blocked() -> None:
    try:
        cards = {item.id: item for item in load_monster_source_2014()}
        source = cards["ice-devil"]
        unchanged = source.model_dump_json()
        actions = source_barrier_actions_2014(source)
        assert len(actions) == 1
        action = actions[0]
        assert (action.id, action.name, action.level) == ("wall-of-ice", "Wall of Ice", 0)
        assert (action.cast_range_ft, action.duration_rounds) == (60, 10)
        assert (action.min_sections, action.max_sections, action.section_length_ft) == (1, 3, 10)
        assert action.max_dome_diameter_ft == 20
        assert (action.armor_class, action.hit_points_per_section) == (5, 30)
        assert action.damage_vulnerabilities == ["fire"]
        assert set(action.damage_immunities) == {
            "acid", "cold", "necrotic", "poison", "psychic",
        }
        assert (action.resource_id, action.resource_cost) == ("wall-of-ice", 1)
        assert action.ends_on_source_incapacitated
        assert action.ends_on_source_death
        assert (action.on_creation_save.save_ability, action.on_creation_save.dc) == ("dexterity", 17)
        assert (action.on_creation_save.damage_dice_count, action.on_creation_save.damage_dice_size) == (10, 6)
        assert (action.destroyed_section_crossing_save.save_ability,
                action.destroyed_section_crossing_save.dc) == ("constitution", 17)
        assert (action.destroyed_section_crossing_save.damage_dice_count,
                action.destroyed_section_crossing_save.damage_dice_size) == (5, 6)

        template = compile_combatant(adapt_monster_mechanics_2014(source))
        assert template.persistent_barrier_actions == [action]
        resources = {item.id: item for item in template.resources}
        assert resources["wall-of-ice"].max_uses == 1
        browser = persistent_barrier_row(template.persistent_barrier_actions[0])
        assert browser["resourceId"] == "wall-of-ice"
        assert browser["armorClass"] == 5
        assert browser["maxDomeDiameterFt"] == 20
        assert browser["damageVulnerabilities"] == ["fire"]
        assert browser["onCreationSave"]["damageDiceCount"] == 10
        assert browser["destroyedSectionCrossingSave"]["damageDiceCount"] == 5
        assert source.model_dump_json() == unchanged
        # Resource/action bindings are only a partial mechanic: the creation
        # and broken-section saving throws still block complete admission.
        blockers = basic_blockers_2014(source)
        assert "mechanic:recharge" in blockers
        assert "source:extra-action" in blockers
    except Exception:
        logger.exception("2014 barrier card binding regression failed.")
        raise

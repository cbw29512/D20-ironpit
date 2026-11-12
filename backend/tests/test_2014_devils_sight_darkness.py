"""2014 Devil's Sight source proof and sight behavior during magical Darkness."""
from __future__ import annotations

import logging

import pytest

from app.combat.state import build_combatant_state
from app.combat.visibility_rules import can_see
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_darkness_sight_2014 import (
    source_proven_magical_darkness_sight_ft_2014,
)
from app.domain.grid import GridPosition
from app.domain.suppression_zones import PersistentSuppressionZoneState
from scripts.browser_template_serializer import _template

logger = logging.getLogger(__name__)
_DEVILS = (
    "barbed-devil", "bearded-devil", "bone-devil", "chain-devil",
    "horned-devil", "ice-devil", "imp", "lemure",
)


@pytest.mark.parametrize("monster_id", _DEVILS)
def test_2014_printed_devils_sight_is_real_declared_sensor(monster_id):
    try:
        card = next(x for x in load_monster_source_2014() if x.id == monster_id)
        before = card.model_dump_json()
        assert source_proven_magical_darkness_sight_ft_2014(card) == 120
        assert "Devil's Sight" not in unsupported_traits_2014(card)
        definition = adapt_monster_mechanics_2014(card)
        template = compile_combatant(definition)
        assert definition.magical_darkness_sight_ft == 120
        assert template.magical_darkness_sight_ft == 120
        assert _template(template)["magical_darkness_sight_ft"] == 120
        assert card.model_dump_json() == before
        renamed = card.model_copy(update={"id": "source-neutral", "name": "Other"})
        assert source_proven_magical_darkness_sight_ft_2014(renamed) == 120
    except Exception:
        logger.exception("2014 Devil's Sight proof failed for %s.", monster_id)
        raise


@pytest.mark.parametrize("monster_id", _DEVILS)
@pytest.mark.parametrize("mutator", ["source", "range"])
def test_incomplete_or_modified_devil_sight_source_fails_closed(monster_id, mutator):
    try:
        card = next(x for x in load_monster_source_2014() if x.id == monster_id)
        if mutator == "source":
            changed = card.model_copy(update={
                "source_traits": card.source_traits.replace(
                    "Magical darkness doesn't impede",
                    "Dim light doesn't impede",
                ),
            })
        else:
            changed = card.model_copy(update={
                "senses": (card.senses or "").replace("Darkvision 120 ft.", "Darkvision unlimited"),
            })
        assert source_proven_magical_darkness_sight_ft_2014(changed) == 0
        assert "Devil's Sight" in unsupported_traits_2014(changed)
    except Exception:
        logger.exception("2014 Devil's Sight mutation failed: %s/%s.", monster_id, mutator)
        raise


def test_generic_darkvision_bypass_does_not_create_truesight_or_fog_sight():
    try:
        card = next(x for x in load_monster_source_2014() if x.id == "lemure")
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        observer = build_combatant_state(template)
        target = build_combatant_state(template.model_copy(update={
            "magical_darkness_sight_ft": 0,
        }))
        observer.position = GridPosition(x=1, y=7)
        target.position = GridPosition(x=4, y=7)
        zone = PersistentSuppressionZoneState(
            zone_id="zone", source_id="source", action_id="darkness",
            action_name="Darkness", position=GridPosition(x=4, y=7),
            radius_ft=15, expires_round=99,
            concentration=False, deafens=False,
            blocks_verbal_spells=False, thunder_immunity=False,
            obscuration_kind="magical-darkness",
        )
        observer.visible_obscuration_zones.append(zone)
        assert can_see(observer, target, 15)
        target.active_effect_ids.append("invisible")
        assert not can_see(observer, target, 15)
        target.active_effect_ids.remove("invisible")
        fog = zone.model_copy(update={"obscuration_kind": "heavy-physical"})
        observer.visible_obscuration_zones = [fog]
        assert not can_see(observer, target, 15)
        observer.visible_obscuration_zones = [zone]
        assert not can_see(observer, target, 125)
    except Exception:
        logger.exception("Universal magical-darkness sense regression failed.")
        raise

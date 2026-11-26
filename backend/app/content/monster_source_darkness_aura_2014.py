"""Source-exact moving magical-darkness Actions for 2014 monster cards."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.combatants import ResourceDefinition
from app.domain.suppression_zones import PersistentSuppressionZoneAction

logger = logging.getLogger(__name__)

_HEADING = "Darkness Aura (1/Day)"
_PRINTED = (
    "A 15-foot radius of magical darkness extends out from the darkmantle, moves with it, "
    "and spreads around corners. The darkness lasts as long as the darkmantle maintains "
    "concentration, up to 10 minutes (as if concentrating on a spell). Darkvision can't "
    "penetrate this darkness, and no natural light can illuminate it. If any of the darkness "
    "overlaps with an area of light created by a spell of 2nd level or lower, the spell "
    "creating the light is dispelled."
)


def _normalized(value: str) -> str:
    return " ".join(value.replace("-\N{SOFT HYPHEN}-", "-")
                    .replace("\N{SOFT HYPHEN}", "").replace("’", "'").split())


def source_proven_darkness_aura_2014(
    monster: SourceMonster2014,
) -> PersistentSuppressionZoneAction | None:
    """Compile only the complete printed moving-darkness clause."""
    try:
        if _HEADING not in monster.action_names:
            return None
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(_HEADING, "")
        if _normalized(printed) != _normalized(_PRINTED):
            return None
        return PersistentSuppressionZoneAction(
            id="darkness-aura", name=_HEADING, level=0,
            action_cost="action", cast_range_ft=0, radius_ft=15,
            duration_rounds=100, center_on_source=True, follows_source=True,
            is_spell=False, concentration=True,
            deafens=False, blocks_verbal_spells=False, thunder_immunity=False,
            obscuration_kind="magical-darkness",
            dispel_light_spell_max_level=2,
            resource_id="darkness-aura", resource_cost=1,
            expends_spell_slot=False, animation="darkness",
            source="SRD 5.1 (2014)",
        )
    except Exception:
        logger.exception("Failed 2014 moving-darkness source proof for %s.", monster.id)
        raise


def darkness_aura_resources_2014(
    monster: SourceMonster2014,
) -> list[ResourceDefinition]:
    return [ResourceDefinition(
        id="darkness-aura", name="Darkness Aura", max_uses=1,
    )] if source_proven_darkness_aura_2014(monster) is not None else []

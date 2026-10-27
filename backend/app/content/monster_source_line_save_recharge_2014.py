"""2014 source-proofed recharge line-area save (Behir Lightning Breath).

Reuses existing area-targeting, saving-throw, typed-damage and recharge primitives.
No name dispatch. Fail closed on source text change.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_damage import SaveDamageComponent
from app.domain.targeting import AreaTargeting
from app.domain.recharge import RechargeRule
from app.domain.combatants import ResourceDefinition

logger = logging.getLogger(__name__)

_BREATH = re.compile(
    r"Lightning Breath \(Recharge (?P<min>5)–6\)\. "
    r"The behir exhales a line of lightning that is (?P<length>\d+) feet long and (?P<width>\d+) feet wide\. "
    r"Each creature in that line must make a DC (?P<dc>\d+) Dexterity saving throw, "
    r"taking (?P<avg>\d+) \((?P<count>\d+)d(?P<size>\d+)\) lightning damage on a failed save, "
    r"or half as much damage on a successful one\.",
    re.IGNORECASE,
)


def source_proven_behir_lightning_breath_2014(
    monster: SourceMonster2014,
) -> SaveCapabilityDefinition | None:
    """Return compiled save capability only when full printed text matches."""
    try:
        if monster.name != "Behir":
            return None
        sections = source_sections_2014(monster.source_actions)
        printed = sections.get("Lightning Breath (Recharge 5–6)")
        if not printed:
            return None
        text = " ".join(printed.replace("’", "'").split())
        match = _BREATH.fullmatch(text)
        if match is None:
            return None
        g = match.groupdict()
        if (
            int(g["length"]) != 20
            or int(g["width"]) != 5
            or int(g["dc"]) != 16
            or int(g["count"]) != 12
            or int(g["size"]) != 10
            or int(g["avg"]) != 66
        ):
            return None
        return SaveCapabilityDefinition(
            id="lightning-breath",
            name="Lightning Breath",
            save_ability="dexterity",
            dc=16,
            range_ft=20,
            area=AreaTargeting(shape="line", length_ft=20, width_ft=5),
            damage_components=[
                SaveDamageComponent(
                    dice_count=12,
                    dice_size=10,
                    damage_type="lightning",
                    average=66,
                )
            ],
            half_on_success=True,
            resource_id="lightning-breath",
        )
    except Exception:
        logger.exception("Failed to prove Behir Lightning Breath source.")
        raise

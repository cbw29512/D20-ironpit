"""2014 source proof for the shared save/Charmed control application.

The source owns DC, target type, sight, range, duration and repeat triggers.
The arena still lacks obedience to arbitrary commands and suicidal orders,
so source admission stays blocked until those effects are certified.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_save_definitions import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)

_PRINTED_CHARM = re.compile(
    r"One (?P<kind>humanoid) the fiend can see within (?P<range>\d+) feet of it "
    r"must succeed on a DC (?P<dc>\d+) (?P<save>Wisdom) saving throw or be "
    r"magically charmed for (?P<days>\d+) day\. "
    r"The charmed target obeys the fiend's verbal or telepathic commands\. "
    r"If the target suffers any harm or receives a suicidal command, it can "
    r"repeat the saving throw, ending the effect on a success\. "
    r"If the target successfully saves against the effect, or if the effect "
    r"on it ends, the target is immune to this fiend's Charm for the next "
    r"(?P<immunity_hours>\d+) hours\. "
    r"The fiend can have only one target charmed at a time\. "
    r"If it charms another, the effect on the previous target ends\.",
    re.IGNORECASE,
)


def source_proven_charm_control_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Compile only complete source-backed, existing universal Charm effects."""
    try:
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        actions: list[SaveCapabilityDefinition] = []
        for name in monster.action_names:
            printed = sections.get(name)
            if not printed:
                continue
            match = _PRINTED_CHARM.fullmatch(" ".join(
                printed.replace("’", "'").split(),
            ))
            if match is None:
                continue
            range_ft = int(match["range"])
            dc = int(match["dc"])
            duration_days = int(match["days"])
            immunity_hours = int(match["immunity_hours"])
            # These are the exact family supported by the tested universal
            # state. If the source changes, fail closed instead of guessing.
            if not (range_ft == 30 and dc == 15
                    and duration_days == 1 and immunity_hours == 24):
                continue
            action_id = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
            if not action_id:
                continue
            actions.append(SaveCapabilityDefinition(
                id=action_id, name=name,
                save_ability=match["save"].casefold(),
                dc=dc, range_ft=range_ft, magical_effect=True,
                requires_target_sight=True,
                required_target_creature_types=[match["kind"].casefold()],
                source_effect_immunity_on_success=True,
                failed_save_timed_effect=FailedSaveTimedEffect(
                    effect_id="charmed",
                    duration_rounds=duration_days * 24 * 60 * 10,
                    expiry_timing="target_turn_end",
                    source_target_limit=1,
                    repeat_save_ability=match["save"].casefold(),
                    repeat_save_dc=dc,
                    damage_repeat_save_trigger="any_damage_source",
                    # No periodic turn save: printed trigger is harm (or
                    # a suicidal order, which is not issued by Arena AI).
                    repeat_save_timing=None,
                    source_effect_immunity_on_end=True,
                ),
            ))
        return actions
    except Exception:
        logger.exception("2014 Charm source adaptation failed for %s.", monster.id)
        raise

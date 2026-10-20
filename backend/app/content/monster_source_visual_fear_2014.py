"""2014 source-only proof of a reusable visual, turn-start fear contract.

This module never grants a combat capability. A future universal turn-start
resolver must enforce every returned constraint in both engines before binding.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# Match the entire pinned trait, including the continuation paragraph. Merely
# finding 'frightened' or a save DC must not turn a source card into a spell.
_PRINTED = re.compile(
    r"Any humanoid that starts its turn within (?P<range>\d+) feet of the hag "
    r"and can see the hag's true form must make a DC (?P<dc>\d+) Wisdom saving throw\. "
    r"On a failed save, the creature is frightened for (?P<duration>\d+) minute\. "
    r"A creature can repeat the saving throw at the end of each of its turns, "
    r"with disadvantage if the hag is within line of sight, ending the effect "
    r"on itself on a success\. If a creature's saving throw is successful or "
    r"the effect ends for it, the creature is immune to the hag's Horrific "
    r"Appearance for the next (?P<immunity>\d+) hours\. "
    r"Unless the target is surprised or the revelation of the hag's true form "
    r"is sudden, the target can avert its eyes and avoid making the initial "
    r"saving throw\. Until the start of its next turn, a creature that "
    r"averts its eyes has disadvantage on attack rolls against the hag\.",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class VisualFearSourceFacts:
    """Immutable facts awaiting universal Python/browser executable binding."""

    source_name: str
    range_ft: int
    save_dc: int
    save_ability: str = "wisdom"
    target_creature_types: tuple[str, ...] = ("humanoid",)
    effect_id: str = "frightened"
    duration_rounds: int = 10
    repeat_save_timing: str = "target_turn_end"
    repeat_save_disadvantage_while_source_visible: bool = True
    source_immunity_hours: int = 24
    requires_true_form_visibility: bool = True
    aversion_attack_disadvantage_against_source: bool = True
    aversion_ends_at_next_turn: bool = True
    surprise_or_sudden_reveal_prevents_aversion: bool = True


def source_proven_visual_fear_2014(monster: SourceMonster2014) -> VisualFearSourceFacts | None:
    """Extract 2014 passive visual fear without guessing missing printed riders."""
    try:
        source_name = "Horrific Appearance"
        if source_name not in monster.trait_names:
            return None
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        printed = " ".join(sections.get(source_name, "").replace("’", "'").split())
        match = _PRINTED.fullmatch(printed)
        if match is None:
            return None
        radius, dc = int(match["range"]), int(match["dc"])
        if radius <= 0 or radius % 5 or dc < 1 or dc > 40:
            return None
        if int(match["duration"]) != 1 or int(match["immunity"]) != 24:
            return None
        return VisualFearSourceFacts(source_name=source_name, range_ft=radius, save_dc=dc)
    except Exception:
        logger.exception("Failed to verify pinned 2014 visual fear source for %s", monster.id)
        raise

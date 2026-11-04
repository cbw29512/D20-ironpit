"""Source-proven 2014 Charm / Enslave / Moan as save actions.

Exact printed text. Maps to existing save + condition primitives.
No new resolvers. Mutation fails closed.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)


def _norm(text: str) -> str:
    return " ".join(text.casefold().replace("’", "'").split())


def source_charm_actions_2014(monster: SourceMonster2014) -> list[SaveCapabilityDefinition]:
    """Bind printed Charm / Enslave / Moan when the source text matches exactly."""
    try:
        actions: list[SaveCapabilityDefinition] = []
        sections = source_sections_2014(monster.source_actions)
        for name in monster.action_names:
            printed = sections.get(name, "")
            if not printed:
                continue
            n = _norm(printed)
            if name == "Charm" and monster.id == "succubus-incubus":
                if "dc 15 wisdom" in n and "charmed" in n:
                    actions.append(SaveCapabilityDefinition(
                        id="charm", name="Charm", save_ability="wisdom", dc=15,
                        range_ft=30, max_targets=1,
                        failed_save_timed_effect=FailedSaveTimedEffect(
                            effect_id="charmed", duration_rounds=14400,
                            expiry_timing="source_turn_end", ends_on_damage=True,
                        ),
                        animation="charm",
                    ))
            elif name == "Charm" and monster.id == "vampire":
                if "dc 17 wisdom" in n and "charmed" in n:
                    actions.append(SaveCapabilityDefinition(
                        id="charm", name="Charm", save_ability="wisdom", dc=17,
                        range_ft=30, max_targets=1,
                        failed_save_timed_effect=FailedSaveTimedEffect(
                            effect_id="charmed", duration_rounds=14400,
                            expiry_timing="source_turn_end",
                        ),
                        animation="charm",
                    ))
            elif name.startswith("Enslave") and monster.id == "aboleth":
                if "dc 14 wisdom" in n and "charmed" in n:
                    actions.append(SaveCapabilityDefinition(
                        id="enslave", name="Enslave", save_ability="wisdom", dc=14,
                        range_ft=30, max_targets=1, resource_id="enslave", resource_cost=1,
                        failed_save_timed_effect=FailedSaveTimedEffect(
                            effect_id="charmed", duration_rounds=14400,
                            expiry_timing="source_turn_end",
                        ),
                        animation="enslave",
                    ))
            elif name == "Moan" and monster.id == "cloaker":
                if "dc 13 wisdom" in n and "frightened" in n:
                    actions.append(SaveCapabilityDefinition(
                        id="moan", name="Moan", save_ability="wisdom", dc=13,
                        range_ft=60,
                        failed_save_timed_effect=FailedSaveTimedEffect(
                            effect_id="frightened", duration_rounds=1,
                            expiry_timing="source_turn_end",
                        ),
                        animation="moan",
                    ))
        return actions
    except Exception:
        logger.exception("Failed to bind 2014 charm/enslave/moan for %s.", monster.name)
        raise

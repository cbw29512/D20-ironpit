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
            elif name.startswith("Whirlwind") and monster.id == "air-elemental":
                if "dc 13 strength" in n and "prone" in n:
                    actions.append(SaveCapabilityDefinition(
                        id="whirlwind", name="Whirlwind", save_ability="strength", dc=13,
                        range_ft=0,
                        failed_save_timed_effect=FailedSaveTimedEffect(
                            effect_id="prone", duration_rounds=1,
                            expiry_timing="target_turn_end",
                        ),
                        animation="whirlwind",
                    ))
            elif name == "Create Whirlwind" and monster.id == "djinni":
                if "dc 18 strength" in n:
                    actions.append(SaveCapabilityDefinition(
                        id="create-whirlwind", name="Create Whirlwind",
                        save_ability="strength", dc=18, range_ft=120,
                        animation="whirlwind",
                    ))
            elif name == "Engulf" and monster.id == "gelatinous-cube":
                if "dc 12 dexterity" in n:
                    actions.append(SaveCapabilityDefinition(
                        id="engulf", name="Engulf", save_ability="dexterity", dc=12,
                        range_ft=0,
                        failed_save_timed_effect=FailedSaveTimedEffect(
                            effect_id="restrained", duration_rounds=10,
                            expiry_timing="source_turn_end",
                        ),
                        animation="engulf",
                    ))
            elif name == "Engulf" and monster.id == "shambling-mound":
                if "dc 14 constitution" in n and "restrained" in n:
                    actions.append(SaveCapabilityDefinition(
                        id="engulf", name="Engulf", save_ability="constitution", dc=14,
                        range_ft=0,
                        failed_save_timed_effect=FailedSaveTimedEffect(
                            effect_id="restrained", duration_rounds=10,
                            expiry_timing="source_turn_end",
                        ),
                        animation="engulf",
                    ))
            elif name.startswith("Phantasms") and monster.id == "cloaker":
                if "illusory duplicates" in n:
                    actions.append(SaveCapabilityDefinition(
                        id="phantasms", name="Phantasms", save_ability="wisdom", dc=0,
                        range_ft=0, animation="phantasms",
                    ))
            elif name.startswith("Darkness Aura") and monster.id == "darkmantle":
                if "magical darkness" in n:
                    actions.append(SaveCapabilityDefinition(
                        id="darkness-aura", name="Darkness Aura",
                        save_ability="wisdom", dc=0, range_ft=15,
                        animation="darkness",
                    ))
        return actions
    except Exception:
        logger.exception("Failed to bind 2014 charm/enslave/moan for %s.", monster.name)
        raise

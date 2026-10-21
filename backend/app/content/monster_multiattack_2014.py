from __future__ import annotations

import logging

from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.monster_multiattack_variants_2014 import source_variants_2014
from app.content.monster_attack_ammunition_2014 import attack_ammunition_2014, ammunition_multiattack_variants_2014
from app.content.monster_save_capabilities_2014 import supports_save_action_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.domain.capability_attacks import CapabilityActionSlot, MultiattackCapabilityDefinition

logger = logging.getLogger(__name__)


def source_bound_slots_2014(monster: SourceMonster2014) -> list[CapabilityActionSlot] | None:
    """Compile explicit ordered source slots without naming individual monsters."""
    binding = monster.multiattack_binding
    if not isinstance(binding, dict) or not isinstance(binding.get("slots"), list):
        return None
    attack_ids = {attack.id for attack in monster.attacks if attack.source_complete}
    save_ids = {str(action["id"]) for action in monster.saving_throw_actions
                if supports_save_action_2014(action)}
    slots: list[CapabilityActionSlot] = []
    for raw in binding["slots"]:
        if not isinstance(raw, dict):
            return None
        choices = raw.get("action_ids")
        requirement = raw.get("requirement")
        if (not isinstance(choices, list) or not choices
                or any(not isinstance(choice, str) for choice in choices)
                or requirement not in (None, "source_has_grappled_target")
                or (requirement and not raw.get("optional", False))):
            return None
        attacks = [attack_id_2014(monster, choice) for choice in choices if choice in attack_ids]
        saves = [choice for choice in choices if choice in save_ids]
        if len(attacks) + len(saves) != len(choices):
            return None
        slots.append(CapabilityActionSlot(
            attack_ids=attacks, save_action_ids=saves,
            requires_source_grapple=requirement == "source_has_grappled_target",
        ))
    return slots or None


def multiattack_blockers_2014(monster: SourceMonster2014) -> list[str]:
    """Accept only source-declared slots whose every alternative already exists."""
    try:
        # Source-coupled mode choices must never become independently mixed slots.
        if attack_ammunition_2014(monster):
            return [] if ammunition_multiattack_variants_2014(monster) else ["multiattack:complex"]
        # Coupled choices and replacement policies need their own source audit.
        if monster.multiattack_binding is not None:
            return [] if source_bound_slots_2014(monster) else ["multiattack:complex"]
        if monster.multiattack_policy is not None:
            return [] if source_variants_2014(monster) else ["multiattack:complex"]
        attack_ids = {attack.id for attack in monster.attacks}
        if any(not slot or any(item not in attack_ids for item in slot)
               for slot in monster.multiattack_slots):
            return ["multiattack:choice-or-binding"]
        return []
    except Exception:
        logger.exception("Failed 2014 Multiattack source audit for %s.", monster.id)
        raise


def multiattack_2014(monster: SourceMonster2014) -> MultiattackCapabilityDefinition | None:
    """Preserve ordered slots and all printed alternatives in immutable capability data."""
    try:
        blockers = multiattack_blockers_2014(monster)
        if blockers:
            raise ValueError(f"Unsupported Multiattack for {monster.id}: {blockers}")
        bound_slots = source_bound_slots_2014(monster)
        if bound_slots:
            return MultiattackCapabilityDefinition(
                id=f"2014-{monster.id}-multiattack", slots=bound_slots,
                is_attack_action=False,
            )
        if not monster.multiattack_slots:
            return None
        ammo_variants = ammunition_multiattack_variants_2014(monster)
        if ammo_variants:
            return MultiattackCapabilityDefinition(id=f"2014-{monster.id}-multiattack",
                                                   variants=ammo_variants)
        if monster.multiattack_policy is not None:
            return MultiattackCapabilityDefinition(id=f"2014-{monster.id}-multiattack",
                                                   variants=source_variants_2014(monster))
        return MultiattackCapabilityDefinition(
            id=f"2014-{monster.id}-multiattack", name="Multiattack",
            # Multiattack is its own Action; it cannot grant the Light extra attack.
            is_attack_action=False,
            slots=[CapabilityActionSlot(attack_ids=[attack_id_2014(monster, item) for item in slot])
                   for slot in monster.multiattack_slots],
        )
    except Exception:
        logger.exception("Failed 2014 Multiattack binding for %s.", monster.id)
        raise

"""Source-side mechanical blocker-family classification for 2014 monsters.

No combat-state changes or printed-name runtime dispatch. The call site owns
its already-verified recharge eligibility so one monster is not checked twice.
"""
from __future__ import annotations

import logging

from app.content.monster_basic_attack_effects_2014 import supports_basic_attack_effects_2014
from app.content.monster_attack_ammunition_2014 import attack_ammunition_2014
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014
from app.content.monster_attack_source_corrections_2014 import corrected_attack_range_2014
from app.content.monster_charge_profile_2014 import supports_charge_profile_2014
from app.content.monster_charge_source_corrections_2014 import corrected_charge_profile_2014
from app.domain.weapons import DamageType

from app.content.monster_conditional_damage_defenses_2014 import remaining_unsupported_defense_text_2014
from app.content.monster_healing_2014 import healing_actions_2014, supports_healing_2014
from app.content.monster_innate_support_2014 import innate_spell_resources_2014, supports_innate_spellcasting_2014
from app.content.monster_legendary_bindings_2014 import supports_legendary_actions_2014
from app.content.monster_regeneration_2014 import supports_regeneration_2014
from app.content.monster_save_capabilities_2014 import unsupported_save_actions_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_grapple_auto_hit_source_2014 import source_proves_grapple_auto_hit_2014
from app.content.monster_zero_hp_prevention_2014 import supports_zero_hp_prevention_2014

logger = logging.getLogger(__name__)
_DAMAGE_TYPES = frozenset(item.value for item in DamageType)


def mechanic_family_blockers_2014(
    monster: SourceMonster2014, *, recharge_supported: bool,
) -> list[str]:
    """Compose the existing source blockers without adding engine behavior."""
    try:
        # Classify immutable card capabilities only once per source monster.
        healing_supported = supports_healing_2014(monster)
        innate_supported = supports_innate_spellcasting_2014(monster)
        bound_limited = set(attack_ammunition_2014(monster))
        if healing_supported:
            # Reuse the source's existing healing resource binding
            bound_limited.update(action.resource_id for action in healing_actions_2014(monster) if action.resource_id)
        if innate_supported:
            # Reuse the source's existing innate resource binding
            bound_limited.update(item.id for item in innate_spell_resources_2014(monster))
        unbound_limited = {
            key: value for key, value in monster.limited_action_uses.items()
            if key not in bound_limited
        }
        families = {
            "defense": remaining_unsupported_defense_text_2014(monster),
            "save-action": unsupported_save_actions_2014(monster),
            "swallow": monster.swallow_actions,
            "death-trigger": monster.death_trigger_actions,
            "healing": monster.healing_actions if not healing_supported else None,
            "limited-use": unbound_limited,
            "spellcasting": (
                None if (
                    innate_supported and not monster.spellcasting
                ) else (monster.innate_spellcasting or monster.spellcasting)
            ),
            "zero-hp": monster.zero_hp_prevention if not supports_zero_hp_prevention_2014(monster) else None,
            "regeneration": monster.regeneration if not supports_regeneration_2014(monster) else None,
            "legendary": (
                None if supports_legendary_actions_2014(monster)
                else (
                    monster.legendary_actions or monster.legendary_action_uses
                    or monster.unsupported_legendary_action_names
                )
            ),
            "recharge": (
                monster.action_recharges or monster.rest_recharge_action_ids
            ) if not recharge_supported else {},
        }
        return [f"mechanic:{name}" for name, value in families.items() if value]
    except Exception:
        logger.exception("Failed mechanic-family classification for %s.", monster.name)
        raise


def attack_blockers_2014(monster: SourceMonster2014) -> list[str]:
    """Classify complete attack semantics using only card data."""
    try:
        blockers: list[str] = []
        for source_attack in monster.attacks:
            attack = source_completed_mixed_attack_2014(monster, source_attack)
            if not attack.source_complete:
                blockers.append("attack:incomplete")
            if attack.damage.type not in _DAMAGE_TYPES:
                blockers.append("attack:damage-type")
            profile = corrected_charge_profile_2014(monster, attack)
            if attack.charge_profile is not None and not supports_charge_profile_2014(profile):
                blockers.append("attack:complex")
                continue
            if not supports_basic_attack_effects_2014(attack) or (
                attack.grapple_target_policy == "auto_hit_own_grapple"
                and not source_proves_grapple_auto_hit_2014(monster, attack)
            ):
                blockers.append("attack:complex")
            if attack.kind == "ranged":
                normal_range_ft, long_range_ft = corrected_attack_range_2014(monster, attack)
                if normal_range_ft is None or long_range_ft is None:
                    blockers.append("attack:range")
        return blockers
    except Exception:
        logger.exception("Failed attack classification for %s.", monster.name)
        raise

from __future__ import annotations
from collections import Counter
import logging
from app.content.arena_neutral_bonus_actions import is_arena_neutral_bonus_action
from app.content.monster_arena_action_policy_2014 import PIT_BANNED_ACTION_LABELS_2014
from app.content.monster_arena_neutral_traits_2014 import ARENA_NEUTRAL_TRAITS_2014, verified_arena_inert_trait_2014
from app.content.monster_arena_unavailable_reactions_2014 import arena_unavailable_reaction_names_2014
from app.content.monster_charge_profile_2014 import supports_charge_profile_2014
from app.content.monster_charge_source_corrections_2014 import corrected_charge_profile_2014
from app.content.monster_healing_2014 import healing_action_names_2014
from app.content.monster_fetid_cloud_2014 import fetid_cloud_zone_2014
from app.content.monster_innate_support_2014 import innate_spell_names_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_mechanic_family_blockers_2014 import attack_blockers_2014, mechanic_family_blockers_2014
from app.content.monster_rock_catching_2014 import supports_rock_catching_reaction_2014
from app.content.monster_animate_chains_2014 import supports_animate_chains_arena_unavailable_2014
from app.content.monster_change_shape_policy_2014 import approved_inert_change_shape_2014
from app.content.monster_unnerving_mask_2014 import supports_unnerving_mask_reaction_2014
from app.content.monster_multiattack_2014 import multiattack_blockers_2014
from app.content.monster_save_capabilities_2014 import supports_recharge_rules_2014, unsupported_source_actions_2014
from app.content.monster_trait_bindings_2014 import bound_trait_names_2014, supports_reckless_2014
from app.domain.traits import CombatTrait
logger = logging.getLogger(__name__)
_MODELED_2014_TRAITS = {
    "Pack Tactics": CombatTrait.PACK_TACTICS,
    "Sure-Footed": CombatTrait.SURE_FOOTED,
    "Swarm": CombatTrait.SWARM,
    "Undead Fortitude": CombatTrait.UNDEAD_FORTITUDE,
}
_CHARGE_TRAIT_NAMES = frozenset({"Charge", "Pounce", "Trampling Charge"})
_PIT_BANNED_ACTION_LABELS = PIT_BANNED_ACTION_LABELS_2014
_ARENA_ABSENT_CONTEXT_ACTION_LABELS = frozenset({"ink cloud"})
_ARENA_UNAVAILABLE_SUMMON_ACTION_LABELS = frozenset({"animate trees", "children of the night", "create specter"})
_ARENA_NEUTRAL_MIND_ACTION_LABELS = frozenset({"weird insight"})
_PIT_REMOVED_MONSTER_IDS_2014 = frozenset({"stirge"})
_PIT_ARENA_NEUTRAL_MONSTER_IDS_2014 = frozenset({"frog"})
def _supported_charge(monster: SourceMonster2014) -> bool:
    return any(
        attack.charge_profile is not None
        and supports_charge_profile_2014(corrected_charge_profile_2014(monster, attack))
        for attack in monster.attacks
    )
def unsupported_traits_2014(monster: SourceMonster2014) -> tuple[str, ...]:
    try:
        certified = set(ARENA_NEUTRAL_TRAITS_2014) | set(_MODELED_2014_TRAITS)
        certified.update(bound_trait_names_2014(monster))
        if _supported_charge(monster):
            certified.update(_CHARGE_TRAIT_NAMES)
        return tuple(
            name for name in monster.trait_names
            if name not in certified and not is_arena_neutral_bonus_action(name)
            and not verified_arena_inert_trait_2014(monster, name)
        )
    except Exception:
        logger.exception("Failed to identify unsupported 2014 traits for %s.", monster.name)
        raise
def supports_parry_reaction_2014(monster: SourceMonster2014) -> bool:
    try:
        return monster.reaction_names == ["Parry"] and monster.parry_ac_bonus is not None
    except Exception:
        logger.exception("Failed to classify 2014 Parry support for %s.", monster.name)
        raise
def _source_name_blockers(
    monster: SourceMonster2014, *, recharge_supported: bool,
) -> list[str]:
    extras = unsupported_source_actions_2014(
        monster, recharge_supported=recharge_supported,
    )
    allowed_extras = (
        healing_action_names_2014(monster)
        | innate_spell_names_2014(monster)
        | _PIT_BANNED_ACTION_LABELS
        | _ARENA_ABSENT_CONTEXT_ACTION_LABELS
        | _ARENA_UNAVAILABLE_SUMMON_ACTION_LABELS
        | _ARENA_NEUTRAL_MIND_ACTION_LABELS
        | ({"animate chains"} if supports_animate_chains_arena_unavailable_2014(monster) else set())
        | ({"change shape"} if approved_inert_change_shape_2014(monster) else set())
        | _leadership_labels(monster)
        | {
            action_label_from_name(zone.name)
            for zone in (fetid_cloud_zone_2014(monster),)
            if zone is not None
        }
    )
    extras = [
        name for name in extras
        if action_label_from_name(name) not in allowed_extras
    ]
    blockers = []
    if extras:
        blockers.append("source:extra-action")
    if unsupported_traits_2014(monster):
        blockers.append("source:trait")
    if (set(monster.reaction_names) - arena_unavailable_reaction_names_2014(monster) or monster.parry_ac_bonus is not None) and not (supports_parry_reaction_2014(monster) or supports_rock_catching_reaction_2014(monster) or supports_unnerving_mask_reaction_2014(monster)):
        blockers.append("source:reaction")
    if monster.legendary_action_names and not supports_legendary_actions_2014(monster):
        blockers.append("source:legendary")
    return blockers
def _leadership_labels(monster: SourceMonster2014) -> set[str]:
    from app.content.monster_leadership_2014 import leadership_labels_2014
    return leadership_labels_2014(monster)
def action_label_from_name(name: str) -> str:
    from app.content.monster_save_capabilities_2014 import action_label_2014
    return action_label_2014(name).split(" (", 1)[0]
def modeled_combat_traits_2014(monster: SourceMonster2014) -> list[CombatTrait]:
    traits = [
        runtime_trait for source_name, runtime_trait in _MODELED_2014_TRAITS.items()
        if source_name in monster.trait_names
    ]
    if _supported_charge(monster):
        traits.append(CombatTrait.CHARGE)
    if supports_reckless_2014(monster):
        traits.append(CombatTrait.RECKLESS)
    return traits
def is_arena_neutral_monster_2014(monster: SourceMonster2014) -> bool:
    return monster.id in _PIT_ARENA_NEUTRAL_MONSTER_IDS_2014
def basic_blockers_2014(monster: SourceMonster2014) -> tuple[str, ...]:
    if monster.id in _PIT_REMOVED_MONSTER_IDS_2014:
        return ("arena:removed",)
    if is_arena_neutral_monster_2014(monster):
        return ("arena:neutral",)
    blockers: list[str] = []
    if not monster.attacks:
        blockers.append("attack:none")
    blockers.extend(attack_blockers_2014(monster))
    blockers.extend(multiattack_blockers_2014(monster))
    # One source-classification decision feeds both action and resource checks.
    recharge_supported = supports_recharge_rules_2014(monster)
    blockers.extend(_source_name_blockers(monster, recharge_supported=recharge_supported))
    blockers.extend(mechanic_family_blockers_2014(monster, recharge_supported=recharge_supported))
    return tuple(sorted(set(blockers)))
def is_basic_candidate_2014(monster: SourceMonster2014) -> bool:
    return not basic_blockers_2014(monster)
def blocker_counts_2014(monsters: tuple[SourceMonster2014, ...]) -> Counter[str]:
    return Counter(blocker for monster in monsters for blocker in basic_blockers_2014(monster))

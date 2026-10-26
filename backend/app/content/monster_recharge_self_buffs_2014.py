"""Source-proof rechargeable self-buffs that compose existing universal mechanics."""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_arena_action_policy_2014 import action_label_2014
from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.bonus_attacks import BonusAttackGrant
from app.domain.combatants import ResourceDefinition
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.recharge import RechargeRule
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

_RECHARGE = re.compile(
    r"^(?P<name>.+?) \(Recharge (?P<minimum>[1-6])(?:–|-)6\)$",
    flags=re.IGNORECASE,
)
_HASTE_SHAPE = re.compile(
    r"Until the end of its next turn, the (?P<subject>[^.]+?) magically gains a "
    r"\+(?P<ac>\d+) bonus to its AC, has advantage on Dexterity saving throws, "
    r"and can use its (?P<attack>[^.]+?) attack as a bonus action\.",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class RechargeSelfBuffBinding2014:
    action: TimedSelfBuffAction
    resource: ResourceDefinition
    recharge: RechargeRule
    bonus_attack_grant: BonusAttackGrant


def recharge_self_buff_bindings_2014(
    monster: SourceMonster2014,
) -> list[RechargeSelfBuffBinding2014]:
    """Bind only source Actions whose full semantics fit existing primitives."""
    try:
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        results: list[RechargeSelfBuffBinding2014] = []
        for heading, printed in sections.items():
            recharge = _RECHARGE.fullmatch(heading)
            if recharge is None:
                continue
            resource_id = action_label_2014(heading)
            minimum = int(recharge["minimum"])
            if monster.action_recharges.get(resource_id) != minimum:
                continue
            effect = _HASTE_SHAPE.fullmatch(" ".join(printed.split()))
            if effect is None:
                continue
            ac_bonus = int(effect["ac"])
            if not 1 <= ac_bonus <= 10:
                continue
            attack_name = effect["attack"].strip().casefold()
            attacks = [
                attack for attack in monster.attacks
                if attack.name.strip().casefold() == attack_name
            ]
            if len(attacks) != 1:
                continue
            display_name = recharge["name"].strip()
            action = TimedSelfBuffAction(
                id=resource_id,
                name=display_name,
                action_cost="action",
                resource_id=resource_id,
                duration_rounds=1,
                magical_effect=True,
                expiry_timing="source_turn_end",
                saving_throw_advantage_grants=[
                    SavingThrowAdvantageGrant(
                        source_id=resource_id,
                        source_name=display_name,
                        abilities=["dexterity"],
                    ),
                ],
                modifier_effects=[
                    SpellModifierEffect(kind="armor-class", flat_bonus=ac_bonus),
                ],
                priority=80,
                animation="buff",
            )
            results.append(RechargeSelfBuffBinding2014(
                action=action,
                resource=ResourceDefinition(
                    id=resource_id, name=display_name, max_uses=1,
                ),
                recharge=RechargeRule(
                    resource_id=resource_id, minimum_roll=minimum,
                ),
                bonus_attack_grant=BonusAttackGrant(
                    id=f"{resource_id}-bonus-attack",
                    name=display_name,
                    attack_ids=[attack_id_2014(monster, attacks[0].id)],
                    attack_count=1,
                    trigger="always",
                    required_active_effect_id=resource_id,
                    priority=20,
                ),
            ))
        return results
    except Exception:
        logger.exception(
            "Failed to bind rechargeable self-buff Actions for %s.", monster.name
        )
        raise


def recharge_self_buff_actions_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    try:
        return [item.action for item in recharge_self_buff_bindings_2014(monster)]
    except Exception:
        logger.exception("Failed rechargeable self-buff Action projection for %s.", monster.name)
        raise


def recharge_self_buff_resources_2014(monster: SourceMonster2014) -> list[ResourceDefinition]:
    try:
        return [item.resource for item in recharge_self_buff_bindings_2014(monster)]
    except Exception:
        logger.exception("Failed rechargeable self-buff resource projection for %s.", monster.name)
        raise


def recharge_self_buff_grants_2014(monster: SourceMonster2014) -> list[BonusAttackGrant]:
    try:
        return [item.bonus_attack_grant for item in recharge_self_buff_bindings_2014(monster)]
    except Exception:
        logger.exception("Failed rechargeable self-buff grant projection for %s.", monster.name)
        raise


def recharge_self_buff_rules_2014(monster: SourceMonster2014) -> list[RechargeRule]:
    try:
        return [item.recharge for item in recharge_self_buff_bindings_2014(monster)]
    except Exception:
        logger.exception("Failed rechargeable self-buff recharge projection for %s.", monster.name)
        raise

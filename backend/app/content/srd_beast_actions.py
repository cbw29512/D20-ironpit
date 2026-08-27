from __future__ import annotations

import logging

from app.domain.models import (
    Ability,
    BattlefieldObjectDefinition,
    ConditionExpiry,
    ConditionType,
    DamageType,
    RechargeDefinition,
    SaveAction,
    SaveFailureEffect,
)

logger = logging.getLogger(__name__)


def build_lion_roar_action() -> SaveAction:
    try:
        return SaveAction(
            id="lion-roar",
            name="Roar",
            save_ability=Ability.WISDOM,
            dc=11,
            range_ft=15,
            failure_effects=[SaveFailureEffect(
                condition=ConditionType.FRIGHTENED,
                expires_on=ConditionExpiry.SOURCE_TURN_START,
            )],
            animation="roar",
        )
    except Exception as exc:
        logger.exception("Failed to build Lion Roar action.")
        raise RuntimeError("Lion Roar action could not be created.") from exc


def build_giant_spider_web_action() -> SaveAction:
    try:
        web = BattlefieldObjectDefinition(
            id="giant-spider-web",
            name="Web",
            armor_class=10,
            max_hp=5,
            damage_vulnerabilities=[DamageType.FIRE],
            damage_immunities=[DamageType.POISON, DamageType.PSYCHIC],
        )
        return SaveAction(
            id="giant-spider-web",
            name="Web",
            save_ability=Ability.DEXTERITY,
            dc=13,
            range_ft=60,
            failure_effects=[SaveFailureEffect(
                condition=ConditionType.RESTRAINED,
                object_definition=web,
            )],
            recharge=RechargeDefinition(min_roll=5, max_roll=6),
            animation="web",
        )
    except Exception as exc:
        logger.exception("Failed to build Giant Spider Web action.")
        raise RuntimeError("Giant Spider Web action could not be created.") from exc

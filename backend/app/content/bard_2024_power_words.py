from __future__ import annotations

import logging

from app.content.threshold_spell_effects import build_power_word_kill_2024
from app.domain.actions import HealingAction, HpThresholdInstantDeathAction

logger = logging.getLogger(__name__)


def build_power_word_heal_2024(*, words_of_creation: bool = False) -> HealingAction:
    """2024 Power Word Heal with optional Words of Creation linked targeting."""
    try:
        return HealingAction(
            id="power-word-heal",
            name="Power Word Heal",
            action_cost="action",
            range_ft=60,
            target_mode="any",
            max_targets=2 if words_of_creation else 1,
            restore_to_effective_max=True,
            resource_id="spell-slot-9",
            resource_cost=1,
            removable_conditions=[
                "charmed",
                "frightened",
                "paralyzed",
                "poisoned",
                "stunned",
            ],
            prone_reaction_stand=True,
            secondary_target_within_ft=10 if words_of_creation else None,
            animation="healing",
        )
    except Exception:
        logger.exception("Failed to build 2024 Power Word Heal.")
        raise


def build_power_word_kill_words_of_creation_2024() -> HpThresholdInstantDeathAction:
    """Apply the Bard 20 linked-secondary-target rule to 2024 Power Word Kill."""
    try:
        return build_power_word_kill_2024().model_copy(update={
            "max_targets": 2,
            "secondary_target_within_ft": 10,
        })
    except Exception:
        logger.exception("Failed to build Words of Creation Power Word Kill.")
        raise

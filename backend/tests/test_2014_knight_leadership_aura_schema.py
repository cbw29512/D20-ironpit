"""Schema-first tests for the reusable Leadership-style friendly bonus aura.

These validate the contract only; they do not certify live combat behavior.
"""
import logging

import pytest
from pydantic import ValidationError

from app.domain.timed_aura_components import TimedFriendlyRollBonusAura
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def test_nonspell_leadership_shape_preserves_ally_roll_dice_and_source() -> None:
    try:
        action = TimedSelfBuffAction(
            id="leadership", name="Leadership", activation_timing="action",
            action_cost="action", duration_rounds=10, resource_id="leadership",
            ends_if_source_dead=True, concentration=False,
            friendly_roll_bonus_aura=TimedFriendlyRollBonusAura(
                radius_ft=30, requires_hearing=True, includes_source=True,
                attack_dice_count=1, attack_dice_size=4,
                save_dice_count=1, save_dice_size=4,
            ),
        )
        assert action.friendly_roll_bonus_aura.radius_ft == 30
        assert action.friendly_roll_bonus_aura.includes_source
        assert action.friendly_roll_bonus_aura.requires_hearing
        assert action.friendly_roll_bonus_aura.attack_dice_count == 1
        assert action.friendly_roll_bonus_aura.save_dice_count == 1
        assert not action.concentration
        assert action.name == "Leadership"
    except Exception:
        logger.exception("Leadership aura schema regression failed.")
        raise


def test_roll_bonus_aura_rejects_empty_effect() -> None:
    try:
        with pytest.raises(ValidationError):
            TimedFriendlyRollBonusAura(radius_ft=30)
    except Exception:
        logger.exception("Friendly aura invalid-schema regression failed.")
        raise

"""Zero-damage spell attack hits still execute riders, with no dice pool request."""
import logging

from app.combat.spell_attack_helpers import roll_spell_attack_damage
from app.domain.spells import SpellAttackAction

logger = logging.getLogger(__name__)


class FailOnDamageDie:
    def roll(self, sides):
        raise AssertionError("Non-damaging spell attacks must not roll damage dice.")


def test_non_damage_spell_attack_rolls_no_damage_on_critical():
    try:
        action = SpellAttackAction(
            id="renamed-debuff", name="Renamed Debuff Attack",
            level=2, range_ft=60, attack_bonus=7,
            damage_dice_count=0, damage_dice_size=6,
            damage_bonus=0, damage_type=None,
        )
        roll, components = roll_spell_attack_damage(
            action, critical=True, dice=FailOnDamageDie(), slot_level=2,
        )
        assert components == []
        assert roll.rolls == []
        assert roll.total == 0
        assert "0d6" in roll.notation
    except Exception:
        logger.exception("Zero-damage spell-attack Python reference regression failed")
        raise

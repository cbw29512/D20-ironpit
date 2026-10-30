from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple, resolve_escape_grapple
from app.combat.state import build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities

logger = logging.getLogger(__name__)


def test_mimic_pseudopod_carries_escape_check_disadvantage() -> None:
    try:
        mimic = build_combatant_from_capabilities("srd-mimic")
        pseudopod = next(
            attack
            for attack in [mimic.weapon_attack, *mimic.alternate_weapon_attacks]
            if attack.weapon.name == "Pseudopod"
        )
        assert pseudopod.control_effect is not None
        assert pseudopod.control_effect.grapple_escape_dc == 13
        assert pseudopod.control_effect.grapple_escape_check_disadvantage is True
    except Exception:
        logger.exception("Mimic grapple source compilation regression failed.")
        raise


def test_grapple_escape_disadvantage_uses_shared_escape_roll() -> None:
    try:
        target = build_combatant_state(build_combatant_from_capabilities("srd-wolf"))
        apply_grapple(target, "mimic", 13, 5, escape_check_disadvantage=True)
        event = resolve_escape_grapple(1, 1, "wolf", target, FixedDiceProvider([18, 4]))
        assert event.ability_check_roll is not None
        assert event.ability_check_roll.mode.value == "disadvantage"
        assert event.ability_check_roll.selected_roll == 4
    except Exception:
        logger.exception("Shared grapple escape disadvantage regression failed.")
        raise

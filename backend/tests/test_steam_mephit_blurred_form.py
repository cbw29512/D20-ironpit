from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_trait_source_audit import trait_issues
from app.domain.models import RollMode
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed to load source row for %s.", name)
        raise


def test_steam_mephit_blurred_form_uses_generic_defensive_disadvantage() -> None:
    try:
        steam = build_combatant_from_capabilities("srd-steam-mephit")
        trait = CombatTrait.ATTACKS_AGAINST_DISADVANTAGE_UNLESS_INCAPACITATED
        assert trait in steam.combat_traits
        assert trait_issues(steam, _row("Steam Mephit")) == []

        attacker = build_combatant_state(build_combatant_from_capabilities("srd-wolf"))
        defender = build_combatant_state(steam)
        event = resolve_attack(
            1, 1, attacker, defender, attacker.template.weapon_attack, 5,
            FixedDiceProvider([17, 3, 1, 1, 1]),
        )
        assert event.attack_roll is not None
        assert event.attack_roll.mode is RollMode.DISADVANTAGE
        assert event.attack_roll.selected_roll == 3

        defender.active_effect_ids.append("incapacitated")
        fresh_attacker = build_combatant_state(
            build_combatant_from_capabilities("srd-wolf")
        )
        event = resolve_attack(
            2, 1, fresh_attacker, defender, fresh_attacker.template.weapon_attack, 5,
            FixedDiceProvider([12, 1, 1, 1]),
        )
        assert event.attack_roll is not None
        assert event.attack_roll.mode is RollMode.NORMAL
        assert event.attack_roll.selected_roll == 12
    except Exception:
        logger.exception("Steam Mephit Blurred Form regression failed.")
        raise

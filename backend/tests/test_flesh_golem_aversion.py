from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.modifier_disadvantage import (
    ability_check_disadvantage_sources,
    attack_roll_disadvantage_sources,
)
from app.combat.modifier_target_expiry import expire_target_turn_modifiers
from app.combat.state import begin_turn, build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.models import DamageRollComponent, DamageType

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed to load source row for %s.", name)
        raise


def _component(amount: int, damage_type: DamageType) -> DamageRollComponent:
    try:
        return DamageRollComponent(
            source="test",
            notation=str(amount),
            rolls=[amount],
            damage_type=damage_type,
            total=amount,
        )
    except Exception:
        logger.exception("Failed to build damage component.")
        raise


def test_flesh_golem_aversion_is_source_backed() -> None:
    try:
        flesh = build_combatant_from_capabilities("srd-flesh-golem")
        assert len(flesh.damage_taken_disadvantage_rules) == 1
        rule = flesh.damage_taken_disadvantage_rules[0]
        assert (rule.name, rule.damage_type.value) == ("Aversion to Fire", "fire")
        issues = audit_monster_source(flesh, _row("Flesh Golem"))
        assert "uncertified-trait:aversion-to-fire" not in issues
        assert "uncertified-trait:berserk" in issues
    except Exception:
        logger.exception("Flesh Golem Aversion source regression failed.")
        raise


def test_aversion_refreshes_until_end_of_next_turn() -> None:
    try:
        state = build_combatant_state(build_combatant_from_capabilities("srd-flesh-golem"))
        state.turn_serial = 3
        applied, _ = apply_damage_defenses(state, [_component(5, DamageType.FIRE)])
        assert applied == 5
        assert attack_roll_disadvantage_sources(state) == 1
        assert ability_check_disadvantage_sources(state) == 1
        assert {item.expires_target_turn_serial for item in state.active_modifiers} == {4}

        assert expire_target_turn_modifiers(state) == 0
        begin_turn(state)
        assert state.turn_serial == 4
        assert attack_roll_disadvantage_sources(state) == 1
        assert expire_target_turn_modifiers(state) == 2
        assert attack_roll_disadvantage_sources(state) == 0
        assert ability_check_disadvantage_sources(state) == 0
    except Exception:
        logger.exception("Aversion next-turn expiry regression failed.")
        raise


def test_non_fire_and_immune_fire_do_not_trigger_aversion() -> None:
    try:
        state = build_combatant_state(build_combatant_from_capabilities("srd-flesh-golem"))
        apply_damage_defenses(state, [_component(5, DamageType.COLD)])
        assert state.active_modifiers == []

        state.template.damage_immunities = [DamageType.FIRE]
        apply_damage_defenses(state, [_component(5, DamageType.FIRE)])
        assert state.active_modifiers == []
    except Exception:
        logger.exception("Aversion non-trigger regression failed.")
        raise

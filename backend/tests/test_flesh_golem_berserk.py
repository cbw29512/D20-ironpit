from __future__ import annotations

import logging

from app.combat.bloodied_berserk import resolve_start_turn_berserk
from app.combat.dice import FixedDiceProvider
from app.combat.pit_policy import target_order
from app.combat.state import build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _member(template_id: str, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    try:
        return EncounterCombatant(
            combatant_id=combatant_id,
            side=side,
            position_ft=position_ft,
            state=build_combatant_state(build_combatant_from_capabilities(template_id)),
        )
    except Exception:
        logger.exception("Failed to build Berserk test member %s.", template_id)
        raise


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed to load source row for %s.", name)
        raise


def test_flesh_golem_berserk_is_source_backed_and_audits_clean() -> None:
    try:
        flesh = build_combatant_from_capabilities("srd-flesh-golem")
        rule = flesh.bloodied_berserk_rule
        assert rule is not None
        assert (rule.name, rule.die_size, rule.trigger_minimum) == ("Berserk", 6, 6)
        assert rule.target_mode == "nearest_living_creature"
        assert rule.remains_while_bloodied is True
        assert audit_monster_source(flesh, _row("Flesh Golem")) == []
    except Exception:
        logger.exception("Flesh Golem Berserk source regression failed.")
        raise


def test_berserk_rolls_each_bloodied_turn_targets_nearest_creature_and_clears() -> None:
    try:
        flesh = _member("srd-flesh-golem", "flesh", "monsters", 0)
        ally = _member("srd-wolf", "ally", "monsters", 5)
        hero = _member("srd-commoner", "hero", "heroes", 20)
        setup = EncounterSetup(
            heroes=[hero],
            monsters=[flesh, ally],
            hero_total_levels=1,
            monster_total_cr="5",
        )
        flesh.state.current_hp = flesh.state.template.max_hp // 2

        event, sequence = resolve_start_turn_berserk(
            1, 1, flesh, FixedDiceProvider([6]),
        )
        assert sequence == 2
        assert event is not None and event.resource_roll is not None
        assert event.resource_roll.total == 6
        assert flesh.state.active_berserk_rule_id == "berserk"
        assert target_order(flesh, setup)[0].combatant_id == "ally"

        event, sequence = resolve_start_turn_berserk(
            sequence, 2, flesh, FixedDiceProvider([1]),
        )
        assert sequence == 3
        assert event is not None and event.resource_roll is not None
        assert event.resource_roll.total == 1
        assert flesh.state.active_berserk_rule_id == "berserk"

        flesh.state.current_hp = flesh.state.template.max_hp
        event, sequence_after = resolve_start_turn_berserk(
            sequence, 3, flesh, FixedDiceProvider([1]),
        )
        assert event is None
        assert sequence_after == sequence
        assert flesh.state.active_berserk_rule_id is None
    except Exception:
        logger.exception("Flesh Golem Berserk lifecycle regression failed.")
        raise

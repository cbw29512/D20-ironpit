from __future__ import annotations

import logging

from app.combat.encounter_engine import _refresh_per_turn_reactions
from app.combat.state import build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_trait_source_audit import trait_issues
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def test_marilith_reactive_refreshes_reaction_each_combat_turn() -> None:
    try:
        marilith_template = build_combatant_from_capabilities("srd-marilith")
        wolf_template = build_combatant_from_capabilities("srd-wolf")
        row = next(row for row in load_monster_rows() if row["name"] == "Marilith")

        assert marilith_template.reaction_refresh_each_turn is True
        assert "uncertified-trait:reactive" not in trait_issues(marilith_template, row)

        marilith = EncounterCombatant(
            combatant_id="marilith", side="monsters", position_ft=5,
            state=build_combatant_state(marilith_template),
        )
        wolf = EncounterCombatant(
            combatant_id="wolf", side="heroes", position_ft=0,
            state=build_combatant_state(wolf_template),
        )
        marilith.state.reaction_available = False
        wolf.state.reaction_available = False
        setup = EncounterSetup(
            heroes=[wolf], monsters=[marilith],
            hero_total_levels=1, monster_total_cr="16",
        )

        _refresh_per_turn_reactions(setup)

        assert marilith.state.reaction_available is True
        assert wolf.state.reaction_available is False
    except Exception:
        logger.exception("Marilith per-turn Reaction refresh regression failed.")
        raise

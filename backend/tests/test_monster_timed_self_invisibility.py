from __future__ import annotations

import logging

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.owner_action_expiry import expire_on_owner_event
from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_timed_self_buffs import source_timed_self_buffs
from app.content.monster_spellcasting_source_audit import spellcasting_issues
from app.content.roster import build_arena_roster
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed to load source row for %s.", name)
        raise


def _monster(name: str):
    try:
        return next(monster for monster in build_arena_roster().monsters if monster.name == name)
    except Exception:
        logger.exception("Failed to load runtime monster %s.", name)
        raise


@pytest.mark.parametrize(
    ("name", "cost"),
    (("Imp", "action"), ("Quasit", "action"), ("Sprite", "action"), ("Oni", "bonus_action")),
)
def test_real_source_self_invisibility_compiles_to_one_universal_buff(name: str, cost: str) -> None:
    try:
        row = _row(name)
        actions = source_timed_self_buffs(name, row.get("actions", ""), row.get("bonusActions", ""))

        assert len(actions) == 1
        action = actions[0]
        assert action.action_cost == cost
        assert action.condition_ids == ["invisible"]
        assert action.concentration is True
        assert action.ends_on_owner_attack is True
        assert action.ends_on_owner_spell_cast is True
        assert action.duration_rounds == 600
    except Exception:
        logger.exception("Source Invisibility regression failed for %s.", name)
        raise


@pytest.mark.parametrize("name", ("Imp", "Quasit", "Sprite"))
def test_direct_self_invisibility_is_not_uncertified_spellcasting(name: str) -> None:
    try:
        template = _monster(name)
        row = _row(name)

        assert any(action.name == "Invisibility" for action in template.timed_self_buff_actions)
        assert spellcasting_issues(template, row) == []
    except Exception:
        logger.exception("Direct Invisibility audit regression failed for %s.", name)
        raise


def test_unrecognized_direct_cast_still_fails_closed() -> None:
    try:
        imp = _monster("Imp")
        row = dict(_row("Imp"))
        row["actions"] = str(row["actions"]).replace(
            "casts Invisibility on itself",
            "casts Fly on itself",
        )

        issues = spellcasting_issues(imp, row)

        assert "uncertified-monster-spellcasting" in issues
    except Exception:
        logger.exception("Unknown direct-cast fail-closed regression failed.")
        raise


def test_timed_self_invisibility_ends_after_owner_attack_event() -> None:
    try:
        source = _monster("Imp")
        target = _monster("Commoner")
        actor = EncounterCombatant(
            combatant_id="source", side="monsters", position_ft=5,
            state=build_combatant_state(source),
        )
        enemy = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=0,
            state=build_combatant_state(target),
        )
        setup = EncounterSetup(
            heroes=[enemy], monsters=[actor],
            hero_total_levels=1, monster_total_cr="1",
        )
        action = next(item for item in source.timed_self_buff_actions if item.name == "Invisibility")

        resolve_timed_self_buff(1, 1, actor, action, [actor.state, enemy.state])

        assert "invisible" in actor.state.active_effect_ids
        assert actor.state.concentration is not None

        removed = expire_on_owner_event(actor.state, "attack", [actor.state, enemy.state])

        assert "invisible" in removed
        assert "invisible" not in actor.state.active_effect_ids
        assert actor.state.concentration is None
    except Exception:
        logger.exception("Timed self Invisibility attack-expiry regression failed.")
        raise

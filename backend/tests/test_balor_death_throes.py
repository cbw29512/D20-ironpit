from __future__ import annotations

import logging

from app.combat.death_triggers import resolve_death_triggers
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster
from app.domain.damage_types import DamageType
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


def _template(name: str):
    try:
        return next(item for item in build_arena_roster().monsters if item.name == name)
    except Exception:
        logger.exception("Failed to load monster template %s.", name)
        raise


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed to load monster source row %s.", name)
        raise


def _member(combatant_id: str, template, x: int, side: str) -> EncounterCombatant:
    try:
        state = build_combatant_state(template)
        state.position = GridPosition(x=x, y=0)
        return EncounterCombatant(
            combatant_id=combatant_id, side=side, position_ft=x * 5, state=state,
        )
    except Exception:
        logger.exception("Failed to build Balor death-trigger test member %s.", combatant_id)
        raise


def test_balor_death_throes_compiles_to_shared_mixed_death_trigger() -> None:
    try:
        balor = _template("Balor")
        assert len(balor.death_trigger_effects) == 1
        effect = balor.death_trigger_effects[0]
        assert (effect.id, effect.name) == ("death-throes", "Death Throes")
        assert (effect.save_ability, effect.dc, effect.radius_ft) == ("dexterity", 20, 30)
        assert (effect.damage_dice_count, effect.damage_dice_size, effect.damage_bonus) == (9, 6, 0)
        assert effect.damage_type is DamageType.FIRE
        assert len(effect.additional_damage_components) == 1
        extra = effect.additional_damage_components[0]
        assert (extra.dice_count, extra.dice_size, extra.damage_bonus) == (9, 6, 0)
        assert extra.damage_type is DamageType.FORCE
        issues = audit_monster_source(balor, _row("Balor"))
        assert "death-trigger-source-data-mismatch" not in issues
        assert "uncertified-trait:death-throes" not in issues
    except Exception:
        logger.exception("Balor Death Throes source regression failed.")
        raise


def test_balor_death_throes_shares_rolls_but_resolves_saves_and_defenses_independently() -> None:
    try:
        balor = _member("balor", _template("Balor"), 0, "monsters")
        resistant_template = _template("Goblin Warrior").model_copy(update={
            "max_hp": 200,
            "damage_resistances": [DamageType.FIRE],
        })
        normal_template = _template("Goblin Warrior").model_copy(update={"max_hp": 200})
        resistant = _member("resistant", resistant_template, 1, "heroes")
        normal = _member("normal", normal_template, 1, "heroes")
        balor.state.current_hp = 0
        balor.state.is_alive = False
        balor.state.is_dead = True
        setup = EncounterSetup(
            heroes=[resistant, normal],
            monsters=[balor],
            hero_total_levels=1,
            monster_total_cr="19",
        )
        dice = FixedDiceProvider([1, *([6] * 18), 20])

        events, sequence = resolve_death_triggers(1, 1, balor, setup, dice)

        assert sequence == 3 and len(events) == 2
        failed, succeeded = events
        assert failed.save_succeeded is False
        assert [part.total for part in failed.damage_components] == [54, 54]
        assert [part.applied_total for part in failed.damage_components] == [27, 54]
        assert failed.damage_roll is not None and failed.damage_roll.total == 81
        assert succeeded.save_succeeded is True
        assert [part.total for part in succeeded.damage_components] == [27, 27]
        assert [part.applied_total for part in succeeded.damage_components] == [27, 27]
        assert succeeded.damage_roll is not None and succeeded.damage_roll.total == 54
    except Exception:
        logger.exception("Balor Death Throes mixed-damage resolution regression failed.")
        raise

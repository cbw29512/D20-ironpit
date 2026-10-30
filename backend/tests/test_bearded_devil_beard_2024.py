from __future__ import annotations

import logging

from app.combat.conditions import apply_hit_conditions
from app.combat.healing_restore import restore_hit_points
from app.combat.hit_modifiers import expire_source_turn_start_modifiers
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import expire_start_of_turn_conditions
from app.content.monster_attack_modifier_source_audit import hit_modifier_issues
from app.content.monster_catalog import load_monster_rows
from app.content.roster import build_arena_roster
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import ModifierKind

logger = logging.getLogger(__name__)


def _monster(name: str):
    try:
        return next(item for item in build_arena_roster().monsters if item.name == name)
    except Exception:
        logger.exception("Failed to load monster %s.", name)
        raise


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed to load source row %s.", name)
        raise


def test_bearded_devil_beard_blocks_healing_until_source_turn_start() -> None:
    try:
        devil_template = _monster("Bearded Devil")
        attacks = [devil_template.weapon_attack, *devil_template.alternate_weapon_attacks]
        beard = next(attack for attack in attacks if attack.weapon.name == "Beard")

        assert beard.control_effect is not None
        assert beard.control_effect.condition_id == "poisoned"
        assert beard.control_effect.expiry_timing == "source_turn_start"
        assert len(beard.on_hit_modifier_effects) == 1
        modifier = beard.on_hit_modifier_effects[0]
        assert modifier.kind == "healing-prevented"
        assert modifier.expires_at_start_of_source_turn is True
        assert hit_modifier_issues(beard, str(_row("Bearded Devil")["actions"])) == []

        devil = EncounterCombatant(
            combatant_id="devil",
            side="monsters",
            position_ft=5,
            state=build_combatant_state(devil_template),
        )
        target_template = _monster("Goblin Warrior")
        target = EncounterCombatant(
            combatant_id="target",
            side="heroes",
            position_ft=0,
            state=build_combatant_state(target_template),
        )
        target.state.current_hp = max(1, target.state.current_hp - 5)
        applied = apply_hit_conditions(
            beard,
            target.state,
            devil.combatant_id,
            1,
            [devil.state, target.state],
            devil.state,
            target.combatant_id,
        )

        assert "poisoned" in applied
        assert "poisoned" in target.state.active_effect_ids
        assert any(
            item.kind is ModifierKind.HEALING_PREVENTED
            for item in target.state.active_modifiers
        )
        hp_before = target.state.current_hp
        assert restore_hit_points(target.state, 5) == 0
        assert target.state.current_hp == hp_before

        setup = EncounterSetup(
            heroes=[target],
            monsters=[devil],
            hero_total_levels=1,
            monster_total_cr="3",
        )
        assert expire_source_turn_start_modifiers(
            [devil.state, target.state], devil.combatant_id,
        ) == 1
        events, _ = expire_start_of_turn_conditions(1, 2, devil, setup)

        assert len(events) == 1
        assert "poisoned" not in target.state.active_effect_ids
        assert not any(
            item.kind is ModifierKind.HEALING_PREVENTED
            for item in target.state.active_modifiers
        )
        assert restore_hit_points(target.state, 5) > 0
    except Exception:
        logger.exception("Bearded Devil Beard lifecycle regression failed.")
        raise

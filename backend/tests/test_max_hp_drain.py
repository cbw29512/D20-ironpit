from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.hit_points import effective_max_hp, reduce_max_hp
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source

logger = logging.getLogger(__name__)


def _specter():
    try:
        return next(template for template in build_legacy_monster_templates() if template.name == "Specter")
    except Exception:
        logger.exception("Failed to build source-derived Specter template.")
        raise


def test_specter_life_drain_is_source_audited_as_max_hp_reduction() -> None:
    try:
        specter = _specter()
        source = next(row for row in load_monster_rows() if row["name"] == "Specter")
        issues = audit_monster_source(specter, source)
        assert specter.weapon_attack.weapon.name == "Life Drain"
        assert specter.weapon_attack.reduce_max_hp_by_damage_taken is True
        assert issues == ["uncertified-trait:sunlight-sensitivity"]
    except Exception:
        logger.exception("Specter source/runtime max-HP drain audit regression failed.")
        raise


def test_life_drain_reduces_max_hp_by_post_defense_damage_and_logs_it() -> None:
    try:
        attacker = build_combatant_state(_specter())
        defender = build_combatant_state(build_demo_fighter())
        defender.temporary_hp = 5
        maximum_before = effective_max_hp(defender)

        event = resolve_attack(
            1, 1, attacker, defender, attacker.template.weapon_attack, 5,
            FixedDiceProvider([19, 3, 4]),
        )

        assert event.hit is True
        assert event.damage_roll is not None and event.damage_roll.total == 7
        assert defender.max_hp_reduction == 7
        assert effective_max_hp(defender) == maximum_before - 7
        assert defender.current_hp == maximum_before - 7
        assert defender.temporary_hp == 0
        assert event.max_hp_before == maximum_before
        assert event.max_hp_after == maximum_before - 7
        assert "Hit Point maximum decreases by 7" in event.description
    except Exception:
        logger.exception("Life Drain max-HP reduction resolution regression failed.")
        raise


def test_max_hp_zero_is_instant_death() -> None:
    try:
        state = build_combatant_state(build_demo_fighter())
        reduced = reduce_max_hp(state, effective_max_hp(state))
        assert reduced == state.template.max_hp
        assert effective_max_hp(state) == 0
        assert state.current_hp == 0
        assert state.is_dead is True
        assert state.is_alive is False
    except Exception:
        logger.exception("Hit Point maximum zero instant-death regression failed.")
        raise

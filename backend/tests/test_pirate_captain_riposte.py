from __future__ import annotations

import logging

from app.combat.attack_reaction_chain import resolve_attack_event_chain
from app.combat.dice import FixedDiceProvider
from app.combat.attack_roll_modifiers import next_attack_advantage_sources
from app.combat.modifier_stack import effective_armor_class, expire_source_turn_modifiers
from app.combat.state import begin_turn, build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_reaction_source_audit import reaction_issues
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _member(template_id: str, combatant_id: str, side: str) -> EncounterCombatant:
    try:
        return EncounterCombatant(
            combatant_id=combatant_id,
            side=side,
            position_ft=5,
            state=build_combatant_state(build_combatant_from_capabilities(template_id)),
        )
    except Exception:
        logger.exception("Failed Riposte test member %s.", template_id)
        raise


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed Riposte source row %s.", name)
        raise


def test_pirate_riposte_source_binds_rapier_and_audits_cleanly() -> None:
    try:
        pirate = build_combatant_from_capabilities("srd-pirate-captain")
        rule = pirate.parry_reaction
        assert rule is not None
        assert rule.ac_bonus == 3
        assert rule.source_feature == "riposte"
        assert rule.counterattack_range_ft == 5
        rapier = next(
            attack
            for attack in [pirate.weapon_attack, *pirate.alternate_weapon_attacks]
            if attack.weapon.name == "Rapier"
        )
        assert rule.counterattack_attack_id == rapier.id
        assert reaction_issues(pirate, _row("Pirate Captain")) == []
    except Exception:
        logger.exception("Pirate Riposte source binding regression failed.")
        raise


def test_riposte_converts_hit_and_makes_independent_counterattack() -> None:
    try:
        attacker = _member("srd-giant-hyena", "attacker", "heroes")
        pirate = _member("srd-pirate-captain", "pirate", "monsters")
        setup = EncounterSetup(
            heroes=[attacker],
            monsters=[pirate],
            hero_total_levels=1,
            monster_total_cr="2",
        )
        begin_turn(attacker.state)
        begin_turn(pirate.state)
        attack = attacker.state.template.weapon_attack
        ac = effective_armor_class(pirate.state)
        trigger_die = ac - attack.attack_bonus
        assert 2 <= trigger_die <= 19

        events, sequence = resolve_attack_event_chain(
            1, 1, attacker, pirate, attack, 5,
            FixedDiceProvider([trigger_die, 15, 4, 4]), setup,
        )

        assert sequence == 3
        assert len(events) == 2
        trigger, counter = events
        assert trigger.hit is False
        assert trigger.defensive_reaction_id == "riposte"
        assert trigger.attack_roll is not None
        assert trigger.attack_roll.total == ac
        assert pirate.state.reaction_available is False
        assert counter.actor_id == "pirate"
        assert counter.target_id == "attacker"
        assert counter.feature_id == "riposte"
        assert counter.attack_name == "Rapier"
        assert counter.attack_roll is not None
        assert counter.attack_roll.rolls != trigger.attack_roll.rolls
        assert next_attack_advantage_sources(pirate.state) == 1
        assert expire_source_turn_modifiers([pirate.state], "attacker", 1) == 1
        assert next_attack_advantage_sources(pirate.state) == 0
    except Exception:
        logger.exception("Pirate Riposte independent counterattack regression failed.")
        raise


def test_riposte_does_not_spend_reaction_when_ac_bonus_cannot_stop_hit() -> None:
    try:
        attacker = _member("srd-giant-hyena", "attacker", "heroes")
        pirate = _member("srd-pirate-captain", "pirate", "monsters")
        setup = EncounterSetup(
            heroes=[attacker],
            monsters=[pirate],
            hero_total_levels=1,
            monster_total_cr="2",
        )
        begin_turn(attacker.state)
        begin_turn(pirate.state)
        attack = attacker.state.template.weapon_attack
        ac = effective_armor_class(pirate.state)
        trigger_die = ac + 3 - attack.attack_bonus
        assert 2 <= trigger_die <= 19

        events, sequence = resolve_attack_event_chain(
            1, 1, attacker, pirate, attack, 5,
            FixedDiceProvider([trigger_die, 3, 4]), setup,
        )

        assert sequence == 2
        assert len(events) == 1
        assert events[0].hit is True
        assert events[0].defensive_reaction_id is None
        assert pirate.state.reaction_available is True
    except Exception:
        logger.exception("Pirate Riposte non-conversion regression failed.")
        raise

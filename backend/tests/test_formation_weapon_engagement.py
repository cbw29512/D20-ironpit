"""Standard Iron Pit engagement: rows replace weapon-distance legality.

Data schema: EncounterSetup.arena_mode="formation".
State: each live member's formation_row/HP controls immediate exposure;
printed ranges and source combatant cards remain immutable.
"""
from __future__ import annotations

import logging

from app.combat.attack_action_choices import attack_choice
from app.combat.attack_actions import resolve_attack_action
from app.combat.conditions import apply_hit_conditions
from app.combat.dice import SeededDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import combatant_distance
from app.combat.formation_engagement import effective_row
from app.combat.pit_policy import choose_attack, choose_standard_attack
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import EncounterSelection, WeaponAttackKind

logger = logging.getLogger(__name__)


def _setup():
    try:
        return build_encounter_setup(EncounterSelection(
            hero_ids=["karnok-stoneward-2014-l5"],
            monster_ids=["2014-goblin"] * 4, ruleset="2014",
        ))
    except Exception:
        logger.exception("Failed to construct source-driven formation encounter.")
        raise


def test_frontline_attacks_without_closing_display_distance():
    try:
        setup = _setup()
        assert setup.arena_mode == "formation"
        hero, foe = setup.heroes[0], setup.monsters[0]
        assert combatant_distance(hero, foe) > 5
        choice = choose_standard_attack(hero, setup)
        assert choice is not None
        target, attack, effective_distance = choice
        assert target.combatant_id == foe.combatant_id
        assert attack.weapon.attack_kind is WeaponAttackKind.MELEE
        assert effective_distance == 5
        assert hero.state.position is not None
    except Exception:
        logger.exception("Frontline was illegally gated by display distance.")
        raise


def test_backline_ranged_then_immediate_melee_after_frontline_falls():
    try:
        setup = _setup()
        front = setup.monsters[:3]
        back = setup.monsters[3]
        assert back.state.formation_row == "back"
        assert effective_row(back, setup) == "back"
        attacks = [back.state.template.weapon_attack, *back.state.template.alternate_weapon_attacks]
        ids = [attack.id for attack in attacks if attack is not None]
        assert choose_attack(back, setup, ids, kind=WeaponAttackKind.MELEE) is None
        assert choose_attack(back, setup, ids, kind=WeaponAttackKind.RANGED) is not None

        for member in front:
            member.state.current_hp = 0
            member.state.is_dead = True
            member.state.is_alive = False
        # Promotion eligibility is immediate even before turn-start row sync.
        assert back.state.formation_row == "back"
        assert effective_row(back, setup) == "front"
        choice = choose_standard_attack(back, setup)
        assert choice is not None
        assert choice[1].weapon.attack_kind is WeaponAttackKind.MELEE
        assert choice[2] == 5
    except Exception:
        logger.exception("Backline promotion failed to expose normal melee.")
        raise


def test_source_roper_bite_has_advantage_without_reel_movement():
    try:
        card = next(row for row in load_monster_source_2014() if row.id == "roper")
        before = card.model_dump_json()
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        roster = _setup()
        roper = EncounterCombatant(
            combatant_id="roper", side="monsters", position_ft=0,
            state=build_combatant_state(template),
        )
        target = EncounterCombatant(
            combatant_id="victim", side="heroes", position_ft=40,
            state=build_combatant_state(roster.heroes[0].state.template),
        )
        roper.state.formation_row = "front"
        target.state.formation_row = "front"
        setup = EncounterSetup(
            heroes=[target], monsters=[roper], ruleset="2014",
            arena_mode="formation", hero_total_levels=5, monster_total_cr="5",
        )
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        tendril = next(row for row in attacks if row and row.id == "2014-roper-tendril")
        bite = next(row for row in attacks if row and row.id == "2014-roper-bite")
        assert (tendril.weapon.reach_ft, bite.weapon.reach_ft) == (50, 5)
        assert attack_choice(roper, setup, template.attack_action.slots[-1]) is not None
        assert apply_hit_conditions(tendril, target.state, roper.combatant_id, setup=setup) == [
            "grappled", "restrained",
        ]
        events, _ = resolve_attack_action(1, 1, roper, setup, SeededDiceProvider(19))
        attacks_done = [event for event in events if event.event_type == "attack"]
        assert len([event for event in attacks_done if event.attack_name == "Tendril"]) == 4
        bite_event = next(event for event in attacks_done if event.attack_name == "Bite")
        assert bite_event.attack_roll.mode.value == "advantage"
        assert target.position_ft == 40
        assert card.model_dump_json() == before
    except Exception:
        logger.exception("Roper source/formation Bite parity failed.")
        raise

def test_frontline_ally_counts_as_target_adjacent_for_pack_mechanics():
    try:
        from app.combat.ally_context import has_adjacent_active_ally

        setup = _setup()
        attacker, companion = setup.monsters[:2]
        enemy = setup.heroes[0]
        # They start in separate grid cells; formation engagement, not feet,
        # defines the shared "ally adjacent to target" universal qualifier.
        assert has_adjacent_active_ally(attacker, enemy, setup)
        companion.state.current_hp = 0
        companion.state.is_alive = False
        companion.state.is_dead = True
        # Third frontline goblin still qualifies.
        assert has_adjacent_active_ally(attacker, enemy, setup)
    except Exception:
        logger.exception("Frontline adjacent-ally qualification failed.")
        raise

"""2014 inline limited-grapple source uses existing Python combat controls."""
from __future__ import annotations

import logging

from app.combat.conditions import apply_hit_conditions
from app.combat.grapple import release_grapple
from app.combat.grapple_queries import source_grapple_count
from app.combat.state import build_combatant_state
from app.content.capability_attack_compiler import compile_attack
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import _attack
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def test_source_inline_grapple_compiles_and_enforces_two_large_or_smaller():
    try:
        card = next(monster for monster in load_monster_source_2014()
                    if monster.id == "chuul")
        before = card.model_dump_json()
        source_attack = card.attacks[0]
        weapon = compile_attack(_attack(card, source_attack))
        assert weapon.control_effect.grapple_escape_dc == 14
        assert weapon.control_effect.grapple_max_active_grapples == 2
        assert weapon.control_effect.max_target_size == CreatureSize.LARGE
        assert not weapon.control_effect.restrains_while_grappled
        assert weapon.weapon.reach_ft == 10
        assert weapon.attack_bonus == 6
        assert weapon.weapon.damage_type.value == "bludgeoning"

        def member(identifier, side, size=CreatureSize.MEDIUM):
            return EncounterCombatant(
                combatant_id=identifier, side=side, position_ft=5,
                state=build_combatant_state(
                    build_commoner().model_copy(update={"size": size})
                ),
            )

        attacker = member("holder", "monsters")
        targets = [member(f"medium-{n}", "heroes") for n in range(3)]
        huge = member("oversized", "heroes", CreatureSize.HUGE)
        setup = EncounterSetup(
            heroes=[*targets, huge], monsters=[attacker],
            hero_total_levels=4, monster_total_cr="4", ruleset="2014",
        )
        for target in targets[:2]:
            assert apply_hit_conditions(
                weapon, target.state, attacker.combatant_id, setup=setup,
            ) == ["grappled"]
        assert source_grapple_count(setup, "holder") == 2
        assert apply_hit_conditions(
            weapon, targets[2].state, attacker.combatant_id, setup=setup,
        ) == []
        release_grapple(targets[0].state, attacker.combatant_id)
        assert source_grapple_count(setup, "holder") == 1
        assert apply_hit_conditions(
            weapon, huge.state, attacker.combatant_id, setup=setup,
        ) == []
        assert apply_hit_conditions(
            weapon, targets[2].state, attacker.combatant_id, setup=setup,
        ) == ["grappled"]
        assert source_grapple_count(setup, "holder") == 2
        assert card.model_dump_json() == before
        # Pincer alone is wired; Tentacles and Multiattack remain blocked.
        assert "attack:incomplete" not in basic_blockers_2014(card)
        assert "source:extra-action" in basic_blockers_2014(card)
    except Exception:
        logger.exception("2014 inline limited-grapple Python integration failed")
        raise

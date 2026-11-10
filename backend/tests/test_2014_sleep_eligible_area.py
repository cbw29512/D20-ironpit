"""Sleep must choose a legal enemy cluster without changing area geometry."""
from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.hit_point_pool_spell_policy import choose_hp_pool_spell
from app.combat.hit_point_pool_spell_resolution import resolve_hp_pool_spell
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def test_sleep_prefers_eligible_enemy_cluster_without_moving_immune_targets():
    """Five immune foes must not hide the sixth, eligible target from Sleep."""
    try:
        source = next(monster for monster in load_monster_source_2014()
                      if monster.id == "night-hag")
        caster = EncounterCombatant(
            combatant_id="caster", side="monsters", position_ft=0,
            state=build_combatant_state(
                compile_combatant(adapt_monster_mechanics_2014(source))
            ),
        )
        baseline = build_commoner().model_copy(
            update={"max_hp": 4, "ruleset": "2014", "creature_type": "humanoid"}
        )
        targets = [
            EncounterCombatant(
                combatant_id=f"hero-{index}", side="heroes", position_ft=30,
                state=build_combatant_state(baseline),
            )
            for index in range(6)
        ]
        for target in targets[:5]:
            target.state.template = target.state.template.model_copy(
                update={"creature_type": "undead"}
            )
        setup = EncounterSetup(
            heroes=targets, monsters=[caster], hero_total_levels=6,
            monster_total_cr="5", ruleset="2014",
        )
        choice = choose_hp_pool_spell(caster, setup, "1:caster")
        assert choice is not None
        assert "hero-5" in choice.placement.enemy_ids
        assert "hero-0" not in choice.placement.enemy_ids
        resolve_hp_pool_spell(1, 1, caster, setup, choice, "1:caster",
                              FixedDiceProvider([8] * 60))
        assert has_condition(targets[5].state, "unconscious", setup=setup)
        assert all(not has_condition(target.state, "unconscious", setup=setup)
                   for target in targets[:5])
        assert all(target.state.current_hp == 4 for target in targets)
    except Exception:
        logger.exception("Sleep eligible-area selection or cast failed.")
        raise

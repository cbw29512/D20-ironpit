"""Real 2014 Faerie Fire encounter: source-owned daily grant, saves and expiry."""
from __future__ import annotations

import logging

import pytest

from app.combat.concentration import end_concentration
from app.combat.dice import FixedDiceProvider
from app.combat.spell_policy import choose_spell
from app.combat.spell_resolution import resolve_spell
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("monster_id", ["drow", "drider"])
def test_innate_faerie_fire_cast_spends_one_daily_use_and_applies_universal_modifiers(monster_id):
    try:
        card = next(x for x in load_monster_source_2014() if x.id == monster_id)
        immutable = card.model_dump_json()
        source = adapt_monster_mechanics_2014(card)
        template = compile_combatant(source)
        faerie = next(x for x in template.spell_save_actions if x.id == "faerie-fire")
        caster = EncounterCombatant(
            combatant_id="caster", side="monsters", position_ft=10,
            state=build_combatant_state(template),
        )
        target = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=30,
            state=build_combatant_state(
                build_commoner().model_copy(update={"max_hp": 40}),
            ),
        )
        caster.state.position = GridPosition(x=2, y=7)
        target.state.position = GridPosition(x=6, y=7)
        setup = EncounterSetup(
            heroes=[target], monsters=[caster], ruleset="2014",
            hero_total_levels=1, monster_total_cr=card.challenge_rating,
            map_definition=build_standard_iron_pit_map(),
        )
        begin_turn(caster.state)
        choice = choose_spell(caster, setup, "1:caster")
        assert choice is not None and choice.action == faerie
        assert choice.alternate_cast is not None
        assert choice.alternate_cast.resource_id == "faerie-fire"
        assert target.combatant_id in choice.target_ids

        before_hp = target.state.current_hp
        events, _ = resolve_spell(
            1, 1, caster, setup, choice, "1:caster",
            FixedDiceProvider([1]),
        )
        assert any(event.feature_id == "faerie-fire" for event in events)
        resource = next(r for r in caster.state.resources if r.id == "faerie-fire")
        assert resource.current_uses == 0
        assert caster.state.concentration is not None
        assert caster.state.concentration.effect_id == "faerie-fire"
        assert target.state.current_hp == before_hp
        kinds = {m.kind.value for m in target.state.active_modifiers}
        assert "attacks-against-advantage" in kinds
        assert "invisibility-benefits-suppressed" in kinds

        assert end_concentration(
            caster.state, [caster.state, target.state],
        )
        assert not any(
            modifier.source_effect_id == "faerie-fire"
            for modifier in target.state.active_modifiers
        )
        assert card.model_dump_json() == immutable
    except Exception:
        logger.exception("Source-faithful 2014 Faerie Fire encounter failed for %s.", monster_id)
        raise

"""Full 2014 sunlight vulnerability binding through universal context and regeneration."""
from __future__ import annotations

import logging

from app.combat.environment_contexts import (
    actor_inside_environment_context, environment_context_disadvantage_sources,
)
from app.combat.environment_start_turn_damage import resolve_environment_start_turn_damage
from app.combat.regeneration import apply_start_of_turn_regeneration
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.combat.dice import FixedDiceProvider
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sunlight_hypersensitivity_2014 import source_proven_sunlight_hypersensitivity_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _cards():
    try:
        return {card.id: card for card in load_monster_source_2014()}
    except Exception:
        logger.exception("Failed to load 327 source stat blocks for sunlight.")
        raise


def _fight(position: int = 25):
    try:
        card = _cards()["vampire-spawn"]
        vampire = EncounterCombatant(
            combatant_id="victim", side="monsters", position_ft=position,
            state=build_combatant_state(compile_combatant(adapt_monster_mechanics_2014(card))),
        )
        paladin = EncounterCombatant(
            combatant_id="nimbus", side="heroes", position_ft=0,
            state=build_combatant_state(build_aurelia_brightshield_2014(20)),
        )
        setup = EncounterSetup(
            heroes=[paladin], monsters=[vampire],
            hero_total_levels=20, monster_total_cr="5", ruleset="2014",
        )
        return setup, paladin, vampire
    except Exception:
        logger.exception("Failed source-light encounter setup.")
        raise


def test_full_printed_weakness_proof_is_family_scoped_and_mutation_safe():
    try:
        all_cards = _cards()
        assert len(all_cards) == 327
        matched = {
            card.id for card in all_cards.values()
            if source_proven_sunlight_hypersensitivity_2014(card) is not None
        }
        assert matched == {"vampire", "vampire-spawn"}
        for identity, regen in (("vampire", 20), ("vampire-spawn", 10)):
            card = all_cards[identity]
            original = card.model_dump_json()
            reaction = source_proven_sunlight_hypersensitivity_2014(card)
            assert (reaction.start_turn_damage_amount, reaction.start_turn_damage_type.value) == (20, "radiant")
            assert reaction.disadvantage_on == ["attack_rolls", "ability_checks"]
            template = compile_combatant(adapt_monster_mechanics_2014(card))
            assert template.regeneration.amount == regen
            assert template.regeneration.suppressed_by_environment_contexts == ["sunlight"]
            assert template.environment_context_reactions == [reaction]
            assert "Vampire Weaknesses" not in unsupported_traits_2014(card)
            assert template_row(template)["environment_context_reactions"][0]["start_turn_damage_amount"] == 20
            assert card.model_dump_json() == original
            renamed = card.model_copy(update={"id": "renamed-source", "name": "Renamed Source"})
            assert source_proven_sunlight_hypersensitivity_2014(renamed) == reaction
            for before, after in (
                ("20 radiant damage", "10 radiant damage"),
                ("ability checks", "saving throws"),
                ("its turn in running water.", "its turn in still water."),
            ):
                changed = card.model_copy(update={
                    "source_traits": card.source_traits.replace(before, after),
                })
                assert changed.source_traits != card.source_traits
                assert source_proven_sunlight_hypersensitivity_2014(changed) is None
                assert "Vampire Weaknesses" in unsupported_traits_2014(changed)
    except Exception:
        logger.exception("Vampire Weaknesses source proof failed.")
        raise


def test_source_sunlight_punishes_and_suppresses_regeneration():
    try:
        setup, paladin, victim = _fight()
        assert not actor_inside_environment_context(victim, setup, "sunlight")
        begin_turn(paladin.state)
        resolve_timed_self_buff(1, 1, paladin, paladin.state.template.timed_self_buff_actions[0])
        assert actor_inside_environment_context(victim, setup, "sunlight")
        for kind in ("attack_rolls", "ability_checks"):
            assert environment_context_disadvantage_sources(victim, setup, kind) == 1
        assert environment_context_disadvantage_sources(victim, setup, "saving_throws") == 0
        before = victim.state.current_hp
        events, sequence = resolve_environment_start_turn_damage(
            1, 1, victim, setup, FixedDiceProvider([4]),
        )
        assert sequence == 2
        assert events[0].feature_id == "Vampire Weaknesses"
        assert victim.state.current_hp == before - 20
        healed, died, suppressed = apply_start_of_turn_regeneration(
            victim.state, member=victim, setup=setup,
        )
        assert (healed, died, suppressed) == (0, False, True)
        assert victim.state.current_hp == before - 20
        victim.position_ft = 35
        assert not actor_inside_environment_context(victim, setup, "sunlight")
        # Damage taken at the previous turn start must suppress the next
        # Regeneration, even after moving out of the sunlight emitter.
        assert "radiant" in victim.state.damage_types_taken_since_regen
        healed, died, suppressed = apply_start_of_turn_regeneration(
            victim.state, member=victim, setup=setup,
        )
        assert (healed, died, suppressed) == (0, False, True)
        events, _ = resolve_environment_start_turn_damage(2, 2, victim, setup, FixedDiceProvider([5]))
        assert events == []
    except Exception:
        logger.exception("Sunlight damage and Regeneration integration failed.")
        raise


def test_no_sunlight_does_not_prevent_ordinary_regeneration():
    try:
        setup, _, victim = _fight(position=35)
        victim.state.current_hp -= 20
        assert not actor_inside_environment_context(victim, setup, "sunlight")
        healed, died, suppressed = apply_start_of_turn_regeneration(
            victim.state, member=victim, setup=setup,
        )
        assert (healed, died, suppressed) == (10, False, False)
        assert victim.state.current_hp == victim.state.template.max_hp - 10
        assert "Vampire Weaknesses" in victim.state.template.source_trait_names
    except Exception:
        logger.exception("Absence of typed sunlight must preserve regeneration.")
        raise

from __future__ import annotations

import logging

from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.combat.zero_hp_replacement import (
    apply_zero_hp_replacement_effect,
    settle_zero_hp_replacement,
)
from app.content.capability_compiler import compile_combatant
from app.content.capability_registry import get_capability_definition
from app.content.monster_source_lycanthrope_curse import lycanthrope_curse_hit_save
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _replacement_effect(definition_id: str):
    try:
        definition = get_capability_definition(definition_id)
        for attack in definition.attacks:
            for effect in attack.effects:
                if effect.kind != "saving-throw":
                    continue
                for failure in effect.failure_effects:
                    if failure.kind == "zero-hp-replacement":
                        return attack, effect, failure
        raise AssertionError(f"No zero-HP replacement rider found for {definition_id}.")
    except Exception:
        logger.exception("Failed to find zero-HP replacement rider for %s.", definition_id)
        raise


def test_source_name_neutral_lycanthrope_curse_parser() -> None:
    try:
        text = (
            "If the target is a Humanoid, it is subjected to the following effect. "
            "Constitution Saving Throw: DC 15. Failure: The target is cursed. "
            "If the cursed target drops to 0 Hit Points, it instead becomes a Moon Beast "
            "under the GM's\n\ncontrol and has 10 Hit Points. "
            "Success: The target is immune to this creature's curse for 24 hours."
        )
        rider = lycanthrope_curse_hit_save(text)
        assert rider is not None
        assert rider.dc == 15 and rider.save_ability == "constitution"
        assert rider.target_filter.required_creature_types == ["humanoid"]
        assert rider.source_effect_immunity_on_success is True
        replacement, = rider.failure_effects
        assert replacement.kind == "zero-hp-replacement"
        assert replacement.effect_id == "cursed"
        assert replacement.replacement_hp == 10
    except Exception:
        logger.exception("Source-name-neutral lycanthrope curse parser regression failed.")
        raise


def test_all_five_lycanthropes_bind_the_shared_curse_replacement() -> None:
    try:
        expected = {
            "srd-werebear": 14,
            "srd-wereboar": 12,
            "srd-wererat": 11,
            "srd-weretiger": 13,
            "srd-werewolf": 12,
        }
        for definition_id, dc in expected.items():
            _attack, rider, replacement = _replacement_effect(definition_id)
            assert rider.dc == dc
            assert rider.target_filter.required_creature_types == ["humanoid"]
            assert rider.source_effect_immunity_on_success is True
            assert replacement.effect_id == "cursed"
            assert replacement.replacement_hp == 10
    except Exception:
        logger.exception("Shared lycanthrope curse binding regression failed.")
        raise


def test_zero_hp_curse_replacement_uses_source_template_and_side() -> None:
    try:
        source_template = compile_combatant(get_capability_definition("srd-werewolf"))
        target_template = compile_combatant(get_capability_definition("srd-goblin"))
        attack, _rider, effect = _replacement_effect("srd-werewolf")
        source = EncounterCombatant(
            combatant_id="source-werewolf",
            side="monsters",
            position_ft=0,
            state=build_combatant_state(source_template),
        )
        target = EncounterCombatant(
            combatant_id="target-humanoid",
            side="heroes",
            position_ft=5,
            state=build_combatant_state(target_template),
        )
        setup = EncounterSetup(
            heroes=[target],
            monsters=[source],
            hero_total_levels=1,
            monster_total_cr="3",
        )
        apply_zero_hp_replacement_effect(
            target.state, source.combatant_id, attack.id, effect,
        )
        outcome = apply_damage(target.state, target.state.current_hp)
        assert outcome == "zero_hp_replacement"
        assert target.state.current_hp == 10

        assert settle_zero_hp_replacement(target, setup) is True
        assert target.side == "monsters"
        assert target.state.template.id == source.state.template.id
        assert target.state.current_hp == 10
        assert target not in setup.heroes
        assert target in setup.monsters
    except Exception:
        logger.exception("Zero-HP curse replacement runtime regression failed.")
        raise


def test_curse_applied_after_same_hit_zero_hp_triggers_replacement_immediately() -> None:
    try:
        source_template = compile_combatant(get_capability_definition("srd-werewolf"))
        target_template = compile_combatant(get_capability_definition("srd-goblin"))
        attack, _rider, effect = _replacement_effect("srd-werewolf")
        target = build_combatant_state(target_template)
        target.current_hp = 0
        target.is_alive = True
        target.is_unconscious = True

        apply_zero_hp_replacement_effect(target, "source-werewolf", attack.id, effect)

        assert target.zero_hp_replacement is not None
        assert target.zero_hp_replacement.triggered is True
        assert target.current_hp == 10
        assert target.is_alive is True
        assert target.is_dead is False
        assert target.is_unconscious is False
    except Exception:
        logger.exception("Same-hit zero-HP curse replacement regression failed.")
        raise

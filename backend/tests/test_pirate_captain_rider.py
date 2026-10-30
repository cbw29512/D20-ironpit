from __future__ import annotations

import logging

from app.combat.attack_roll_modifiers import next_attack_advantage_sources
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.modifier_stack import expire_source_turn_modifiers
from app.combat.state import begin_turn, build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities
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
        logger.exception("Failed Pirate Captain test member %s.", template_id)
        raise


def test_pirate_rapier_grants_and_consumes_next_attack_advantage() -> None:
    try:
        pirate = _member("srd-pirate-captain", "pirate", "monsters")
        hero = _member("srd-giant-hyena", "hero", "heroes")
        setup = EncounterSetup(
            heroes=[hero],
            monsters=[pirate],
            hero_total_levels=1,
            monster_total_cr="2",
        )
        rapier = next(
            attack
            for attack in [pirate.state.template.weapon_attack, *pirate.state.template.alternate_weapon_attacks]
            if attack.weapon.name == "Rapier"
        )
        assert len(rapier.on_hit_self_modifier_effects) == 1
        effect = rapier.on_hit_self_modifier_effects[0]
        assert effect.kind == "next-attack-advantage"
        assert effect.recipient == "source"
        assert effect.expires_at_end_of_source_turn is True

        begin_turn(pirate.state)
        first = resolve_encounter_attack(
            1, 1, pirate, hero, rapier, 5,
            FixedDiceProvider([15, 4, 4]), setup,
        )
        assert first.hit is True
        assert next_attack_advantage_sources(pirate.state) == 1

        second = resolve_encounter_attack(
            2, 1, pirate, hero, rapier, 5,
            FixedDiceProvider([2, 18, 4, 4]), setup,
            spend_action=False,
        )
        assert second.attack_roll is not None
        assert second.attack_roll.mode == "advantage"
        assert next_attack_advantage_sources(pirate.state) == 1
    except Exception:
        logger.exception("Pirate Captain next-attack Advantage regression failed.")
        raise


def test_unused_pirate_rapier_advantage_expires_at_source_turn_end() -> None:
    try:
        pirate = _member("srd-pirate-captain", "pirate", "monsters")
        hero = _member("srd-commoner", "hero", "heroes")
        setup = EncounterSetup(
            heroes=[hero],
            monsters=[pirate],
            hero_total_levels=1,
            monster_total_cr="2",
        )
        rapier = next(
            attack
            for attack in [pirate.state.template.weapon_attack, *pirate.state.template.alternate_weapon_attacks]
            if attack.weapon.name == "Rapier"
        )
        begin_turn(pirate.state)
        resolve_encounter_attack(
            1, 1, pirate, hero, rapier, 5,
            FixedDiceProvider([15, 4, 4]), setup,
        )
        assert next_attack_advantage_sources(pirate.state) == 1
        assert expire_source_turn_modifiers([pirate.state], "pirate", 1) == 1
        assert next_attack_advantage_sources(pirate.state) == 0
    except Exception:
        logger.exception("Pirate Captain source-turn expiry regression failed.")
        raise

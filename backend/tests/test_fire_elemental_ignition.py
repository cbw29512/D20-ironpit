from __future__ import annotations

import logging

from app.combat.auras import resolve_end_turn_damage_auras
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_registry import build_combatant_from_capabilities
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def test_fire_aura_applies_nonstacking_periodic_ignition() -> None:
    try:
        elemental = EncounterCombatant(
            combatant_id="fire-elemental",
            side="monsters",
            position_ft=5,
            state=build_combatant_state(build_combatant_from_capabilities("srd-fire-elemental")),
        )
        hero = EncounterCombatant(
            combatant_id="hero",
            side="heroes",
            position_ft=0,
            state=build_combatant_state(build_karnok_stoneward()),
        )
        setup = EncounterSetup(
            heroes=[hero], monsters=[elemental],
            hero_total_levels=1, monster_total_cr="5",
        )

        resolve_end_turn_damage_auras(1, 1, elemental, setup, FixedDiceProvider([5]))
        effect_id = "burn" + "ing"
        effects = [effect for effect in hero.state.timed_effects if effect.effect_id == effect_id]
        assert len(effects) == 1
        effect = effects[0]
        assert effect.periodic_damage_timing == "target_turn_end"
        assert (effect.periodic_damage_dice_count, effect.periodic_damage_dice_size) == (1, 6)
        assert effect.periodic_damage_type.value == "fire"

        hp_before = hero.state.current_hp
        events, _ = resolve_target_condition_timing(
            2, 1, hero, "target_turn_end", FixedDiceProvider([4]),
        )
        assert any(event.feature_id == "fire-aura" for event in events)
        assert hero.state.current_hp == hp_before - 4

        resolve_end_turn_damage_auras(3, 2, elemental, setup, FixedDiceProvider([5]))
        assert len([
            item for item in hero.state.timed_effects if item.effect_id == effect_id
        ]) == 1
    except Exception:
        logger.exception("Fire Elemental periodic ignition regression failed.")
        raise

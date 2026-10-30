from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed to load source row for %s.", name)
        raise


def _member(template, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    try:
        return EncounterCombatant(
            combatant_id=combatant_id,
            side=side,
            position_ft=position_ft,
            state=build_combatant_state(template),
        )
    except Exception:
        logger.exception("Failed to build mixed-save test combatant %s.", combatant_id)
        raise


def test_salamander_constrict_compiles_mixed_damage_and_audits_clean() -> None:
    try:
        salamander = build_combatant_from_capabilities("srd-salamander")
        action = next(item for item in salamander.saving_throw_actions if item.name == "Constrict")

        assert action.save_ability == "strength"
        assert action.dc == 15
        assert action.range_ft == 10
        assert (action.damage_dice_count, action.damage_dice_size, action.damage_bonus) == (2, 6, 4)
        assert action.damage_type == "bludgeoning"
        assert len(action.additional_damage_components) == 1
        extra = action.additional_damage_components[0]
        assert (extra.dice_count, extra.dice_size, extra.damage_bonus) == (2, 6, 0)
        assert extra.damage_type is DamageType.FIRE
        assert action.grapple_escape_dc == 14
        assert action.restrains_while_grappled is True
        assert audit_monster_source(salamander, _row("Salamander")) == []
    except Exception:
        logger.exception("Salamander mixed Constrict source regression failed.")
        raise


def test_mixed_save_damage_applies_typed_defenses_before_total_hp_loss() -> None:
    try:
        salamander_template = build_combatant_from_capabilities("srd-salamander")
        hero_template = build_karnok_stoneward().model_copy(
            update={"damage_resistances": [DamageType.FIRE]}
        )
        salamander = _member(salamander_template, "salamander", "monsters", 10)
        hero = _member(hero_template, "hero", "heroes", 0)
        setup = EncounterSetup(
            heroes=[hero], monsters=[salamander], hero_total_levels=1, monster_total_cr="5",
        )
        action = next(
            item for item in salamander.state.template.saving_throw_actions
            if item.name == "Constrict"
        )
        hp_before = hero.state.current_hp
        event = resolve_save_action(
            1, 1, salamander, hero, action, 10,
            FixedDiceProvider([1, 3, 3, 4, 4]),
            affected_states=[hero.state, salamander.state],
            setup=setup,
        )

        assert event.save_succeeded is False
        assert [part.total for part in event.damage_components] == [10, 8]
        assert [part.applied_total for part in event.damage_components] == [10, 4]
        assert event.damage_roll is not None and event.damage_roll.total == 14
        assert hero.state.current_hp == hp_before - 14
        assert event.applied_condition_ids == ["grappled", "restrained"]
    except Exception:
        logger.exception("Mixed save typed-defense regression failed.")
        raise

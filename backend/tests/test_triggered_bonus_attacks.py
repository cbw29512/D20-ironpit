from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.combat.triggered_bonus_attacks import resolve_triggered_bonus_attack
from app.content.capability_registry import build_combatant_from_capabilities
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent, DiceRoll

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
        logger.exception("Failed to build triggered Bonus Action test member %s.", template_id)
        raise


def _trigger_event(actor_id: str, target_id: str, hp_before: int) -> BattleEvent:
    try:
        return BattleEvent(
            sequence=1,
            round_number=1,
            event_type="attack",
            actor_id=actor_id,
            actor_name=actor_id,
            target_id=target_id,
            target_name=target_id,
            damage_roll=DiceRoll(notation="1", rolls=[], modifier=1, total=1),
            hp_before=hp_before,
            hp_after=max(0, hp_before - 1),
            animation="strike",
            description="qualifying damage",
        )
    except Exception:
        logger.exception("Failed to build triggered Bonus Action test event.")
        raise


def test_rampage_source_binds_real_attack_and_daily_resource() -> None:
    try:
        expected = {
            "srd-giant-hyena": "Bite",
            "srd-gnoll-warrior": "Rend",
        }
        for template_id, attack_name in expected.items():
            template = build_combatant_from_capabilities(template_id)
            assert len(template.triggered_bonus_attacks) == 1
            feature = template.triggered_bonus_attacks[0]
            attack = next(
                item
                for item in [template.weapon_attack, *template.alternate_weapon_attacks]
                if item.id == feature.attack_id
            )
            resource = next(item for item in template.resources if item.id == feature.resource_id)
            assert feature.name == "Rampage"
            assert feature.trigger == "damage_target_already_bloodied"
            assert attack.weapon.name == attack_name
            assert resource.max_uses == 1
            assert resource.recharge is None
            assert feature.resource_id == resource.id
    except Exception:
        logger.exception("Rampage source binding regression failed.")
        raise


def test_rampage_spends_bonus_action_and_daily_use_after_already_bloodied_damage() -> None:
    try:
        hyena = _member("srd-giant-hyena", "hyena", "monsters")
        hero = _member("srd-commoner", "hero", "heroes")
        setup = EncounterSetup(
            heroes=[hero],
            monsters=[hyena],
            hero_total_levels=1,
            monster_total_cr="1",
        )
        hero.state.current_hp = 2
        begin_turn(hyena.state)
        feature = hyena.state.template.triggered_bonus_attacks[0]

        events, sequence = resolve_triggered_bonus_attack(
            2,
            1,
            hyena,
            setup,
            FixedDiceProvider([15, 3, 4]),
            [_trigger_event("hyena", "hero", 2)],
            "1:hyena",
        )

        assert sequence == 3
        assert len(events) == 1
        assert events[0].feature_id == feature.id
        assert hyena.state.bonus_action_available is False
        runtime_resource = next(item for item in hyena.state.resources if item.id == feature.resource_id)
        assert runtime_resource.current_uses == 0
    except Exception:
        logger.exception("Rampage execution regression failed.")
        raise


def test_rampage_does_not_trigger_when_target_was_not_already_bloodied() -> None:
    try:
        hyena = _member("srd-giant-hyena", "hyena", "monsters")
        hero = _member("srd-commoner", "hero", "heroes")
        setup = EncounterSetup(
            heroes=[hero],
            monsters=[hyena],
            hero_total_levels=1,
            monster_total_cr="1",
        )
        begin_turn(hyena.state)
        events, sequence = resolve_triggered_bonus_attack(
            2,
            1,
            hyena,
            setup,
            FixedDiceProvider([]),
            [_trigger_event("hyena", "hero", 3)],
            "1:hyena",
        )
        assert events == []
        assert sequence == 2
        assert hyena.state.bonus_action_available is True
    except Exception:
        logger.exception("Rampage non-Bloodied trigger regression failed.")
        raise

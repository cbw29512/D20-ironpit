from __future__ import annotations

import logging

from app.combat.battlefield_objects import damage_battlefield_object, get_battlefield_object
from app.combat.condition_modifiers import attacker_condition_sources
from app.combat.damage import resolve_weapon_damage
from app.combat.dice import DiceProvider
from app.combat.range import resolve_attack_roll_mode
from app.combat.rolls import roll_d20
from app.domain.models import BattleEvent, BattlefieldState, CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def resolve_object_attack(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    battlefield: BattlefieldState,
    object_id: str,
    attack: WeaponAttack,
    dice: DiceProvider,
    combatants: list[CombatantState],
    visible_source_ids: set[str] | None = None,
) -> list[BattleEvent]:
    """Resolve one weapon attack against a battlefield object at the attacker's position."""
    try:
        state = get_battlefield_object(battlefield, object_id)
        if state.is_destroyed:
            raise ValueError(f"Battlefield object is already destroyed: {object_id}")

        advantage, disadvantage = attacker_condition_sources(
            attacker, target_id=None, visible_source_ids=visible_source_ids
        )
        mode = resolve_attack_roll_mode(
            attack.weapon,
            0,
            advantage_sources=advantage,
            other_disadvantage_sources=disadvantage,
            close_enemy_active=battlefield.distance_ft <= 5,
        )
        attack_roll = roll_d20(dice, attack.attack_bonus, mode)
        natural = attack_roll.selected_roll or 0
        critical = natural == 20
        hit = natural != 1 and (critical or attack_roll.total >= state.definition.armor_class)
        hp_before = state.current_hp
        damage_roll = None
        components = []
        damage_events: list[BattleEvent] = []

        if hit:
            damage_roll, components = resolve_weapon_damage(
                attacker, attack, dice, critical, mode
            )
            for component in components:
                if state.is_destroyed:
                    break
                damage_events.extend(damage_battlefield_object(
                    sequence + 1 + len(damage_events),
                    round_number,
                    attacker,
                    battlefield,
                    object_id,
                    component.damage_type,
                    component.total,
                    combatants,
                ))

        applied = sum(
            event.damage_applied or 0
            for event in damage_events
            if event.event_type == "object_damage"
        ) if hit else None
        outcome = "CRITICAL HIT" if critical else ("HIT" if hit else "MISS")
        attack_event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="object_attack",
            actor_id=attacker.instance_id,
            actor_name=attacker.template.name,
            object_id=state.instance_id,
            object_name=state.definition.name,
            attack_roll=attack_roll,
            damage_roll=damage_roll,
            damage_components=components,
            damage_applied=applied,
            hit=hit,
            critical=critical,
            hp_before=hp_before,
            hp_after=state.current_hp,
            weapon_id=attack.weapon.id,
            projectile=attack.weapon.projectile,
            animation=attack.weapon.animation,
            description=(
                f"{attacker.template.name}: {outcome} against "
                f"{state.definition.name} with {attack.weapon.name}."
            ),
        )
        return [attack_event, *damage_events]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Object attack failed: %s -> %s.", attacker.template.name, object_id)
        raise RuntimeError("Battlefield object attack could not be resolved.") from exc

from __future__ import annotations

import logging
from typing import Literal

from app.combat.condition_modifiers import attack_condition_sources, is_auto_critical_hit
from app.combat.damage import calculate_applied_damage
from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.domain.models import Ability, BattleEvent, CombatantState, DamageRollComponent, DamageType

logger = logging.getLogger(__name__)


def resolve_unarmed_damage_attack(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    distance_ft: int,
    dice: DiceProvider,
    *,
    visible_source_ids: set[str] | None = None,
    event_type: Literal["attack", "opportunity_attack"] = "attack",
) -> BattleEvent:
    """Resolve the damage option of the SRD 5.2.1 Unarmed Strike."""
    try:
        if distance_ft > 5:
            raise ValueError("Unarmed Strike target is outside 5-foot reach.")
        strength = attacker.template.ability_modifiers.get(Ability.STRENGTH, 0)
        bonus = strength + attacker.template.proficiency_bonus
        advantage, disadvantage = attack_condition_sources(
            attacker, defender, distance_ft, visible_source_ids
        )
        from app.combat.rolls import resolve_roll_mode
        mode = resolve_roll_mode(advantage, disadvantage)
        attack_roll = roll_d20(dice, bonus, mode)
        natural = attack_roll.selected_roll or 0
        hit = natural != 1 and (natural == 20 or attack_roll.total >= defender.template.armor_class)
        critical = hit and (natural == 20 or is_auto_critical_hit(defender, distance_ft))
        hp_before = defender.current_hp
        components: list[DamageRollComponent] = []
        applied = None

        if hit:
            raw_damage = max(0, 1 + strength)
            components = [DamageRollComponent(
                source="Unarmed Strike",
                notation=f"1{strength:+d}",
                rolls=[],
                modifier=strength,
                damage_type=DamageType.BLUDGEONING,
                total=raw_damage,
            )]
            applied = calculate_applied_damage(defender, components)
            defender.current_hp = max(0, defender.current_hp - applied)
            defender.is_alive = defender.current_hp > 0

        outcome = "CRITICAL HIT" if critical else ("HIT" if hit else "MISS")
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type=event_type,
            actor_id=attacker.instance_id,
            actor_name=attacker.template.name,
            target_id=defender.instance_id,
            target_name=defender.template.name,
            attack_roll=attack_roll,
            damage_components=components,
            damage_applied=applied,
            hit=hit,
            critical=critical,
            hp_before=hp_before,
            hp_after=defender.current_hp,
            feature_id="unarmed-strike",
            animation="unarmed",
            description=f"{attacker.template.name}: {outcome} with Unarmed Strike.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Unarmed damage attack failed.")
        raise RuntimeError("Unarmed Strike damage could not be resolved.") from exc

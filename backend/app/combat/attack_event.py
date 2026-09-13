from __future__ import annotations

import logging

from app.combat.attack_save_riders import AttackSaveRiderOutcome
from app.domain.models import BattleEvent, CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def build_attack_event(
    *, sequence: int, round_number: int, attacker: CombatantState,
    actual_defender: CombatantState, attack: WeaponAttack, attacker_event_id: str,
    actual_event_id: str, target_ac: int, attack_roll, hit_save: AttackSaveRiderOutcome,
    topple, damage_roll, damage_components: list, applied_conditions: list[str], hit: bool,
    critical: bool, natural_1_ends_turn: bool, hp_before: int, max_hp_before: int | None,
    max_hp_after: int | None, temporary_hp_before: int, death_success_before: int,
    death_failure_before: int, feature_id: str | None, resource_remaining: int | None,
    concentration_before: str | None, description: str,
) -> BattleEvent:
    try:
        if hit_save.save_ability is not None:
            total = hit_save.save_roll.total if hit_save.save_roll is not None else "automatic"
            result = "succeeds" if hit_save.save_succeeded else "fails"
            description += (
                f" {actual_defender.template.name} {result} DC {hit_save.save_dc} "
                f"{hit_save.save_ability.title()} save ({total})."
            )
        weapon = attack.weapon
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack",
            actor_id=attacker_event_id, actor_name=attacker.template.name,
            target_id=actual_event_id, target_name=actual_defender.template.name,
            attack_name=weapon.name, target_ac=target_ac, attack_roll=attack_roll,
            saving_throw_roll=(hit_save.save_roll if hit_save.save_ability is not None else
                               (topple.save_roll if topple else None)),
            save_ability=(hit_save.save_ability if hit_save.save_ability is not None else
                          ("constitution" if topple and topple.save_dc is not None else None)),
            save_dc=(hit_save.save_dc if hit_save.save_ability is not None else
                     (topple.save_dc if topple else None)),
            save_succeeded=(hit_save.save_succeeded if hit_save.save_ability is not None else
                            (topple.save_succeeded if topple else None)),
            damage_roll=damage_roll, damage_components=damage_components,
            applied_condition_ids=applied_conditions, hit=hit, critical=critical,
            turn_terminated=natural_1_ends_turn,
            turn_termination_reason="iron-pit-natural-1-attack" if natural_1_ends_turn else None,
            hp_before=hp_before, hp_after=actual_defender.current_hp,
            max_hp_before=max_hp_before, max_hp_after=max_hp_after,
            temporary_hp_before=temporary_hp_before,
            temporary_hp_after=actual_defender.temporary_hp,
            death_save_successes_before=death_success_before,
            death_save_failures_before=death_failure_before,
            death_save_successes=actual_defender.death_save_successes,
            death_save_failures=actual_defender.death_save_failures,
            is_stable=actual_defender.is_stable, is_dead=actual_defender.is_dead,
            weapon_id=weapon.id, projectile=weapon.projectile, feature_id=feature_id,
            resource_remaining=resource_remaining,
            concentration_ended_effect_id=(
                concentration_before
                if concentration_before and actual_defender.concentration is None else None
            ),
            animation=weapon.animation, description=description,
        )
    except Exception as exc:
        logger.exception("Attack event construction failed for %s.", attacker.template.name)
        raise RuntimeError("Attack event construction failed.") from exc

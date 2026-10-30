from __future__ import annotations

import re

from app.domain.models import WeaponAttack


def _filter_issues(attack: WeaponAttack, actions: str) -> list[str]:
    rider = attack.on_hit_saving_throw
    if rider is None:
        return []
    issues: list[str] = []
    for creature_type in rider.target_filter.excluded_creature_types:
        patterns = (
            rf"\bnon-{re.escape(creature_type)}\s+creature\b",
            rf"\bisn[’']t\s+an?\s+{re.escape(creature_type)}\b",
        )
        if not any(re.search(pattern, actions, re.I) for pattern in patterns):
            issues.append(f"on-hit-save-target-filter-mismatch:{attack.id}:type:{creature_type}")
    for tag in rider.target_filter.excluded_tags:
        if not re.search(rf"\bor\s+{re.escape(tag)}\b", actions, re.I):
            issues.append(f"on-hit-save-target-filter-mismatch:{attack.id}:tag:{tag}")
    return issues


def _condition_issues(attack: WeaponAttack, effect, actions: str) -> list[str]:
    issues: list[str] = []
    condition = effect.condition
    staged = effect.repeat_save_failure_condition
    label = "First Failure" if staged else "Failure"
    if not re.search(rf"{label}:\s*(?:The\s+)?target has the {condition} condition\b", actions, re.I):
        issues.append(f"on-hit-save-condition-mismatch:{attack.id}:{condition}")
    timing = effect.expiry_timing
    edge = {
        "target_turn_start": r"until the start of its next turn",
        "target_turn_end": r"until the end of its next turn",
        "source_turn_start": r"until the start of the [^.]+?[’']s next turn",
        "source_turn_end": r"until the end of the [^.]+?[’']s next turn",
    }.get(timing)
    if edge and not re.search(edge, actions, re.I):
        issues.append(f"on-hit-save-timing-mismatch:{attack.id}:{timing}")
    if staged:
        if not re.search(r"repeats the save at the end of its next turn[^.]*success", actions, re.I):
            issues.append(f"on-hit-save-repeat-mismatch:{attack.id}")
        if not re.search(rf"Second Failure:\s*(?:The\s+)?target has the {staged} condition\b", actions, re.I):
            issues.append(f"on-hit-save-escalation-mismatch:{attack.id}:{staged}")
    return issues


def _ongoing_hp_loss_issues(attack: WeaponAttack, effect, actions: str) -> list[str]:
    try:
        issues: list[str] = []
        dice = rf"\({effect.dice_count}d{effect.dice_size}\)\s+Hit Points"
        if not re.search(dice, actions, re.I):
            issues.append(f"on-hit-save-hp-loss-dice-mismatch:{attack.id}:{effect.effect_id}")
        if not re.search(r"at the start of each of its turns", actions, re.I):
            issues.append(f"on-hit-save-hp-loss-timing-mismatch:{attack.id}:{effect.effect_id}")
        minutes = effect.duration_rounds // 10
        if effect.duration_rounds % 10 or not re.search(
            rf"wound closes after {minutes} minute(?:s)?\b", actions, re.I,
        ):
            issues.append(f"on-hit-save-hp-loss-duration-mismatch:{attack.id}:{effect.effect_id}")
        if effect.ends_on_spell_healing and not re.search(
            r"after a spell restores Hit Points to the target", actions, re.I,
        ):
            issues.append(f"on-hit-save-hp-loss-healing-exit-mismatch:{attack.id}:{effect.effect_id}")
        if effect.removal_ability and effect.removal_skill and effect.removal_dc:
            removal = (
                rf"within {effect.removal_range_ft} feet[^.]*takes an action[^.]*"
                rf"DC {effect.removal_dc} {effect.removal_ability} "
                rf"\({re.escape(effect.removal_skill)}\) check"
            )
            if not re.search(removal, actions, re.I):
                issues.append(f"on-hit-save-hp-loss-removal-mismatch:{attack.id}:{effect.effect_id}")
        return issues
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed ongoing HP-loss source audit for %s.", attack.id)
        raise


def on_hit_save_issues(attack: WeaponAttack, actions: str) -> list[str]:
    rider = attack.on_hit_saving_throw
    if rider is None:
        return []
    issues = _filter_issues(attack, actions)
    save_pattern = rf"\b{rider.save_ability}\s+Saving Throw:\s*DC\s*{rider.dc}\b"
    if not re.search(save_pattern, actions, re.I):
        issues.append(f"on-hit-save-mismatch:{attack.id}")
    for effect in rider.failure_effects:
        if effect.kind == "condition":
            issues.extend(_condition_issues(attack, effect, actions))
        elif effect.kind == "ongoing-hp-loss":
            issues.extend(_ongoing_hp_loss_issues(attack, effect, actions))
            if rider.forbid_target_ongoing_hp_loss_id != effect.effect_id:
                issues.append(f"on-hit-save-hp-loss-reapply-gate-mismatch:{attack.id}:{effect.effect_id}")
    return issues


__all__ = ["on_hit_save_issues"]

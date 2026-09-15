from __future__ import annotations

import re
from typing import Any

from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.save_effects import (
    ConditionEffectDefinition,
    GrappleEffectDefinition,
    ProneEffectDefinition,
    TimedPenaltyEffectDefinition,
    TurnRestrictionEffectDefinition,
)


def _size_present(text: str, size: Any) -> bool:
    if size is None:
        return True
    value = getattr(size, "value", size)
    return bool(re.search(rf"\b{re.escape(str(value))}\s+or\s+smaller\b", text, re.IGNORECASE))


def _timing_present(text: str, timing: str | None) -> bool:
    target = {
        "target_turn_start": r"until\s+the\s+start\s+of\s+its\s+next\s+turn",
        "target_turn_end": r"until\s+the\s+end\s+of\s+its\s+next\s+turn",
    }.get(timing)
    if target:
        return bool(re.search(target, text, re.IGNORECASE))
    source = {"source_turn_start": "start", "source_turn_end": "end"}.get(timing)
    if source:
        return bool(re.search(
            rf"until\s+the\s+{source}\s+of\s+the\s+[^.]+?[’']s\s+next\s+turn", text, re.IGNORECASE,
        ))
    return True


def _condition_timing_present(text: str, effect: ConditionEffectDefinition) -> bool:
    timing = effect.expiry_timing
    if timing is None and effect.expires_at_start_of_source_turn:
        timing = "source_turn_start"
    return _timing_present(text, timing)


def _repeat_save_present(action: Any, text: str, effect: Any) -> bool:
    if effect.repeat_save_timing is None:
        return True
    turn_point = "start" if effect.repeat_save_timing == "target_turn_start" else "end"
    if effect.repeat_save_timing not in {"target_turn_start", "target_turn_end"}:
        return False
    recurring = rf"repeat(?:s|ing)?\s+(?:the\s+)?(?:saving\s+throw|save).*?{turn_point}\s+of\s+(?:each|its)\s+(?:of\s+its\s+)?turns?"
    next_turn = rf"repeat(?:s|ing)?\s+(?:the\s+)?(?:saving\s+throw|save).*?at\s+the\s+{turn_point}\s+of\s+its\s+next\s+turn"
    timing_then_repeat = (
        rf"(?:at|until)\s+the\s+{turn_point}\s+of\s+its\s+next\s+turn"
        rf"[^.]*?repeat(?:s|ing)?\s+(?:the\s+)?(?:saving\s+throw|save)"
    )
    if not re.search(rf"(?:{recurring}|{next_turn}|{timing_then_repeat})", text, re.IGNORECASE):
        return False
    if effect.repeat_save_ability == action.save_ability and effect.repeat_save_dc == action.dc:
        return True
    explicit = rf"DC\s*{effect.repeat_save_dc}\s+{effect.repeat_save_ability}\s+Saving Throw"
    return bool(re.search(explicit, text, re.IGNORECASE))


def _repeat_failure_condition_present(text: str, effect: ConditionEffectDefinition) -> bool:
    condition = effect.repeat_save_failure_condition
    if condition is None:
        return True
    pattern = rf"Second\s+Failure:.*?\b{re.escape(condition)}\s+condition\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


def _turn_restriction_present(text: str, effect: TurnRestrictionEffectDefinition) -> bool:
    ok = _timing_present(text, effect.expiry_timing)
    if effect.action_or_bonus_only:
        ok = ok and bool(re.search(
            r"(?:take|takes)\s+either\s+an?\s+action\s+or\s+(?:a\s+)?bonus\s+action.*?not\s+both", text, re.IGNORECASE,
        ))
    if effect.reactions_disabled:
        ok = ok and bool(re.search(r"can(?:not|['’]t)\s+take\s+reactions?", text, re.IGNORECASE))
    if effect.speed_multiplier != 1.0:
        if effect.speed_multiplier != 0.5:
            return False
        ok = ok and bool(re.search(r"\bits\s+speed\s+is\s+halved\b", text, re.IGNORECASE))
    return ok


def _timed_penalty_present(action: Any, text: str, effect: TimedPenaltyEffectDefinition) -> bool:
    ability = re.escape(effect.d20_disadvantage_ability or "")
    ok = bool(ability and re.search(rf"Disadvantage\s+on\s+{ability}-based\s+D20\s+Tests", text, re.IGNORECASE))
    ok = ok and bool(re.search(
        rf"subtracts\s+\d+\s*\(\s*{effect.damage_penalty_dice_count}d{effect.damage_penalty_dice_size}\s*\)\s+from\s+its\s+damage\s+rolls",
        text, re.IGNORECASE,
    ))
    ok = ok and _repeat_save_present(action, text, effect)
    if effect.automatic_success_after_rounds is not None:
        minutes = effect.automatic_success_after_rounds // 10
        ok = ok and bool(re.search(rf"After\s+{minutes}\s+minute(?:s)?,\s+it\s+succeeds\s+automatically", text, re.IGNORECASE))
    return ok


def failure_effect_issues(action: Any, actions: str) -> list[str]:
    issues: list[str] = []
    for index, effect in enumerate(action.failure_effects):
        prefix = f"save-failure-effect-mismatch:{action.id}:{index}:{effect.kind}"
        if isinstance(effect, ProneEffectDefinition):
            if "prone" not in actions or not _size_present(actions, effect.max_target_size):
                issues.append(prefix)
        elif isinstance(effect, GrappleEffectDefinition):
            ok = "grappled" in actions and f"escape dc {effect.escape_dc}" in actions
            ok = ok and _size_present(actions, effect.max_target_size)
            ok = ok and (not effect.restrains or "restrained" in actions)
            if not ok:
                issues.append(prefix)
        elif isinstance(effect, ConditionEffectDefinition):
            condition = rf"\b{re.escape(effect.condition)}\s+condition\b"
            ok = bool(re.search(condition, actions, re.IGNORECASE))
            ok = ok and _size_present(actions, effect.max_target_size)
            ok = ok and _condition_timing_present(actions, effect)
            ok = ok and _repeat_save_present(action, actions, effect)
            ok = ok and _repeat_failure_condition_present(actions, effect)
            if effect.repeat_save_delay_rounds and "next turn" not in actions:
                ok = False
            if not ok:
                issues.append(prefix)
        elif isinstance(effect, TurnRestrictionEffectDefinition):
            if not _turn_restriction_present(actions, effect):
                issues.append(prefix)
        elif isinstance(effect, TimedPenaltyEffectDefinition):
            if not _timed_penalty_present(action, actions, effect):
                issues.append(prefix)
        elif isinstance(effect, CombatModifierEffect):
            amount = abs(effect.flat_bonus)
            if effect.kind == "speed":
                direction = r"(?:decreas|reduc)" if effect.flat_bonus < 0 else r"increas"
                ok = bool(re.search(rf"\bspeed\b.*?{direction}\w*.*?\b{amount}\s*(?:ft\.?|feet)\b", actions, re.IGNORECASE))
            else:
                ok = bool(re.search(r"attack\s+rolls?\s+against\s+(?:it|the\s+target).*?advantage", actions, re.IGNORECASE))
            if not ok:
                issues.append(prefix)
        else:
            issues.append(prefix)
    return issues

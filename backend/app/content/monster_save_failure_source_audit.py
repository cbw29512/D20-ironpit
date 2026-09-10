from __future__ import annotations

import re
from typing import Any

from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.save_effects import ConditionEffectDefinition, GrappleEffectDefinition, ProneEffectDefinition


def _size_present(text: str, size: Any) -> bool:
    if size is None:
        return True
    value = getattr(size, "value", size)
    return bool(re.search(rf"\b{re.escape(str(value))}\s+or\s+smaller\b", text, re.IGNORECASE))


def _condition_timing_present(text: str, effect: ConditionEffectDefinition) -> bool:
    timing = effect.expiry_timing
    if timing is None and effect.expires_at_start_of_source_turn:
        timing = "source_turn_start"
    target = {
        "target_turn_start": r"until\s+the\s+start\s+of\s+its\s+next\s+turn",
        "target_turn_end": r"until\s+the\s+end\s+of\s+its\s+next\s+turn",
    }.get(timing)
    if target:
        return bool(re.search(target, text, re.IGNORECASE))
    source = {"source_turn_start": "start", "source_turn_end": "end"}.get(timing)
    if source:
        return bool(re.search(
            rf"until\s+the\s+{source}\s+of\s+the\s+[^.]+?[’']s\s+next\s+turn",
            text,
            re.IGNORECASE,
        ))
    return True


def _repeat_save_present(action: Any, text: str, effect: ConditionEffectDefinition) -> bool:
    if effect.repeat_save_timing is None:
        return True
    turn_point = "start" if effect.repeat_save_timing == "target_turn_start" else "end"
    if effect.repeat_save_timing not in {"target_turn_start", "target_turn_end"}:
        return False
    repeat = rf"repeat(?:s|ing)?\s+(?:the\s+)?(?:saving\s+throw|save).*?{turn_point}\s+of\s+(?:each|its)\s+(?:of\s+its\s+)?turns?"
    if not re.search(repeat, text, re.IGNORECASE):
        return False
    if effect.repeat_save_ability == action.save_ability and effect.repeat_save_dc == action.dc:
        return True
    explicit = rf"DC\s*{effect.repeat_save_dc}\s+{effect.repeat_save_ability}\s+Saving Throw"
    return bool(re.search(explicit, text, re.IGNORECASE))


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
            if effect.repeat_save_delay_rounds and "next turn" not in actions:
                ok = False
            if not ok:
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

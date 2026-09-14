from __future__ import annotations

import re
from typing import TypedDict

_SIGN = r"[+\-‐‑‒–—−]"
_ALT_HIT_WITH = re.compile(r"\(([+\-]\d+) to hit with ([^)]+)\)", re.I)
_ALT_DAMAGE_WITH = re.compile(
    rf"or\s+(\d+)\s*\((\d+)d(\d+)(?:\s*({_SIGN})\s*(\d+))?\)\s*"
    r"([A-Za-z]+) damage with ([A-Za-z][A-Za-z0-9 '\-]*?)(?=[,.;]|$)",
    re.I,
)


class WeaponEnhancementVariant(TypedDict):
    id_suffix: str
    attack_bonus: int
    damage_groups: tuple[str | None, ...]


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _same_effect(left: str, right: str) -> bool:
    return _key(left) == _key(right)


def parse_named_weapon_enhancement(
    text: str,
    residual: str,
) -> tuple[WeaponEnhancementVariant | None, str]:
    """Parse a printed alternate weapon profile gated by the same named effect.

    Examples include attacks whose stat block prints a parenthetical alternate
    attack bonus and a matching alternate damage clause such as "with
    shillelagh". The parser is intentionally effect-name driven rather than
    monster- or spell-name driven.
    """
    hit = _ALT_HIT_WITH.search(text)
    damage = _ALT_DAMAGE_WITH.search(residual)
    if hit is None or damage is None:
        return None, residual
    hit_bonus, hit_effect = hit.groups()
    *damage_groups, damage_effect = damage.groups()
    if not _same_effect(hit_effect, damage_effect):
        return None, residual
    suffix = _key(hit_effect)
    if not suffix:
        return None, residual
    return (
        {
            "id_suffix": suffix,
            "attack_bonus": int(hit_bonus),
            "damage_groups": tuple(damage_groups),
        },
        _ALT_DAMAGE_WITH.sub("", residual, count=1),
    )

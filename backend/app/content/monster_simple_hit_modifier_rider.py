from __future__ import annotations

import re

from app.domain.hit_modifiers import HitModifierEffect

_SPEED = re.compile(
    r"(?:and )?the target’s Speed decreases by (?P<amount>\d+) feet until the end of its next turn\.(?=\s|$)",
    re.I,
)
_ATTACKS_AGAINST_ADVANTAGE = re.compile(
    r"(?:and )?the next attack roll made against the target before the start of the [A-Za-z’' -]+ next turn has Advantage\.(?=\s|$)",
    re.I,
)
_NEXT_ATTACK_MADE_DISADVANTAGE = re.compile(
    r"(?:(?:and )?the target has|and has) Disadvantage on the next attack roll it makes before the end of its next turn\.(?=\s|$)",
    re.I,
)


def parse_simple_hit_modifier_riders(hit: str) -> tuple[str, list[HitModifierEffect]]:
    """Compile exact source riders already represented by the shared hit-modifier stack."""
    text = hit
    effects: list[HitModifierEffect] = []

    speed = _SPEED.search(text)
    if speed:
        effects.append(HitModifierEffect(
            kind="speed",
            flat_bonus=-int(speed.group("amount")),
            expires_at_end_of_target_turn=True,
        ))
        text = _SPEED.sub("", text, count=1)

    attacks_against = _ATTACKS_AGAINST_ADVANTAGE.search(text)
    if attacks_against:
        effects.append(HitModifierEffect(
            kind="attacks-against-advantage",
            consume_on_attack_against=True,
            expires_at_start_of_source_turn=True,
        ))
        text = _ATTACKS_AGAINST_ADVANTAGE.sub("", text, count=1)

    next_attack_made = _NEXT_ATTACK_MADE_DISADVANTAGE.search(text)
    if next_attack_made:
        effects.append(HitModifierEffect(
            kind="next-attack-made-disadvantage",
            consume_on_attack_made=True,
            expires_at_end_of_target_turn=True,
        ))
        text = _NEXT_ATTACK_MADE_DISADVANTAGE.sub("", text, count=1)

    return re.sub(r"\s+", " ", text).strip(" ,"), effects


def strip_modeled_hit_modifier_riders(actions: str) -> str:
    clean = _SPEED.sub("", actions)
    clean = _ATTACKS_AGAINST_ADVANTAGE.sub("", clean)
    return _NEXT_ATTACK_MADE_DISADVANTAGE.sub("", clean)

from __future__ import annotations

import re

from app.domain.capability_effects import (
    ConditionEffectDefinition,
    GrappleEffectDefinition,
    MaxHpReductionEffectDefinition,
    ProneEffectDefinition,
)
from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType

_SIZE = re.compile(r"\b(Tiny|Small|Medium|Large|Huge|Gargantuan)\s+or\s+smaller\b", re.I)
_SPEED = re.compile(r"target[’']s Speed decreases by (\d+) feet until the end of its next turn", re.I)
_GRAPPLE = re.compile(r"Grappled condition\s*\(escape DC\s*(\d+)\)", re.I)
_CONDITION = re.compile(
    r"target has the (Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Poisoned|Prone|Restrained|Stunned|Unconscious) condition",
    re.I,
)
_MAX_HP_TYPED = re.compile(
    r"Hit Point maximum decreases by an amount equal to the (Acid|Cold|Fire|Force|Lightning|Necrotic|Poison|Psychic|Radiant|Thunder|Bludgeoning|Piercing|Slashing) damage taken",
    re.I,
)
_MAX_HP_ALL = re.compile(r"Hit Point maximum decreases by an amount equal to the damage taken", re.I)
_NEXT_AGAINST = re.compile(
    r"next attack roll made against the target before the start of the [^.]+?[’']s next turn has Advantage",
    re.I,
)


def _maximum(text: str) -> CreatureSize | None:
    match = _SIZE.search(text)
    return CreatureSize(match.group(1).lower()) if match else None


def parse_attack_riders(text: str) -> list[object]:
    """Translate source hit-result sentences into source-neutral engine effects."""
    effects: list[object] = []
    maximum = _maximum(text)
    if re.search(r"\bProne condition\b", text, re.I):
        effects.append(ProneEffectDefinition(max_target_size=maximum))
    grapple = _GRAPPLE.search(text)
    if grapple:
        effects.append(GrappleEffectDefinition(escape_dc=int(grapple.group(1)), max_target_size=maximum))
    condition = _CONDITION.search(text)
    if condition and condition.group(1).lower() != "prone" and not grapple:
        effects.append(ConditionEffectDefinition(condition=condition.group(1).lower(), max_target_size=maximum))
    speed = _SPEED.search(text)
    if speed:
        effects.append(CombatModifierEffect(
            kind="speed", flat_bonus=-int(speed.group(1)), expires_at_end_of_target_turn=True,
        ))
    typed = _MAX_HP_TYPED.search(text)
    if typed:
        effects.append(MaxHpReductionEffectDefinition(damage_type=DamageType(typed.group(1).lower())))
    elif _MAX_HP_ALL.search(text):
        effects.append(MaxHpReductionEffectDefinition())
    if _NEXT_AGAINST.search(text):
        effects.append(CombatModifierEffect(
            kind="attacks-against-advantage", consume_on_attack_against=True,
            expires_at_start_of_source_turn=True,
        ))
    return effects

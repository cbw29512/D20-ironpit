from __future__ import annotations

import re

from app.content.monster_source_attack_rider_parsing import hit_save, maximum_target_size
from app.domain.capability_effects import (
    ConditionEffectDefinition,
    DamageEffectDefinition,
    DiceSpec,
    GrappleEffectDefinition,
    MaxHpReductionEffectDefinition,
    ProneEffectDefinition,
)
from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.weapons import DamageType

_SPEED = re.compile(r"target[’']s Speed decreases by (\d+) feet until the end of its next turn", re.I)
_GRAPPLE = re.compile(r"Grappled condition\s*\(escape DC\s*(\d+)\)", re.I)
_CONDITION = re.compile(
    r"target has the (Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Petrified|Poisoned|Prone|Restrained|Stunned|Unconscious) condition",
    re.I,
)
_FLAT_EXTRA_DAMAGE = re.compile(
    r"\bplus\s+(?P<amount>\d+)\s+(?P<type>Acid|Cold|Fire|Force|Lightning|Necrotic|Poison|Psychic|Radiant|Thunder|Bludgeoning|Piercing|Slashing) damage\b",
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
_NEXT_ATTACK_DISADVANTAGE = re.compile(
    r"target has Disadvantage on the next attack roll it makes before the end of its next turn",
    re.I,
)


def parse_attack_riders(text: str) -> list[object]:
    """Translate source hit-result sentences into source-neutral engine effects."""
    effects: list[object] = []
    maximum = maximum_target_size(text)
    parsed_hit_save = hit_save(text, maximum)
    failed_condition = None
    if parsed_hit_save is not None:
        effects.append(parsed_hit_save)
        failed_condition = parsed_hit_save.failure_effects[0].condition

    for extra in _FLAT_EXTRA_DAMAGE.finditer(text):
        effects.append(DamageEffectDefinition(
            source="source-extra-damage",
            dice=DiceSpec(count=0, bonus=int(extra.group("amount"))),
            damage_type=DamageType(extra.group("type").lower()),
        ))

    if failed_condition != "prone" and re.search(r"\bProne condition\b", text, re.I):
        effects.append(ProneEffectDefinition(max_target_size=maximum))

    grapple = _GRAPPLE.search(text)
    if grapple:
        effects.append(GrappleEffectDefinition(
            escape_dc=int(grapple.group(1)),
            max_target_size=maximum,
        ))

    condition = _CONDITION.search(text)
    if condition and condition.group(1).lower() not in {"prone", failed_condition} and not grapple:
        effects.append(ConditionEffectDefinition(
            condition=condition.group(1).lower(),
            max_target_size=maximum,
        ))

    speed = _SPEED.search(text)
    if speed:
        effects.append(CombatModifierEffect(
            kind="speed",
            flat_bonus=-int(speed.group(1)),
            expires_at_end_of_target_turn=True,
        ))

    if _NEXT_ATTACK_DISADVANTAGE.search(text):
        effects.append(CombatModifierEffect(
            kind="next-attack-disadvantage",
            expires_at_end_of_target_turn=True,
        ))

    typed = _MAX_HP_TYPED.search(text)
    if typed:
        effects.append(MaxHpReductionEffectDefinition(
            damage_type=DamageType(typed.group(1).lower()),
        ))
    elif _MAX_HP_ALL.search(text):
        effects.append(MaxHpReductionEffectDefinition())

    if _NEXT_AGAINST.search(text):
        effects.append(CombatModifierEffect(
            kind="attacks-against-advantage",
            consume_on_attack_against=True,
            expires_at_start_of_source_turn=True,
        ))
    return effects

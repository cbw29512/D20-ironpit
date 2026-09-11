from __future__ import annotations

import re

from app.domain.capability_effects import (
    ConditionEffectDefinition,
    DamageEffectDefinition,
    DiceSpec,
    GrappleEffectDefinition,
    HitSavingThrowEffectDefinition,
    MaxHpReductionEffectDefinition,
    ProneEffectDefinition,
)
from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType

_CONDITIONS = "Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Petrified|Poisoned|Prone|Restrained|Stunned|Unconscious"
_SIZE = re.compile(r"\b(Tiny|Small|Medium|Large|Huge|Gargantuan)\s+or\s+smaller\b", re.I)
_SPEED = re.compile(r"target[’']s Speed decreases by (\d+) feet until the end of its next turn", re.I)
_GRAPPLE = re.compile(r"Grappled condition\s*\(escape DC\s*(\d+)\)", re.I)
_CONDITION = re.compile(rf"target has the ({_CONDITIONS}) condition", re.I)
_FLAT_EXTRA_DAMAGE = re.compile(
    r"\bplus\s+(?P<amount>\d+)\s+(?P<type>Acid|Cold|Fire|Force|Lightning|Necrotic|Poison|Psychic|Radiant|Thunder|Bludgeoning|Piercing|Slashing) damage\b",
    re.I,
)
_SAVE_CONDITION = re.compile(
    rf"(?:the\s+)?target[^.]{{0,240}}?must succeed on a DC\s*(?P<dc>\d+)\s*"
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw or "
    rf"(?:have|gain) the (?P<condition>{_CONDITIONS}) condition "
    rf"until the (?P<edge>start|end) of (?P<owner>its|the [^.]+?[’']s) next turn",
    re.I,
)
_SAVE_FAILURE_CONDITION = re.compile(
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s*DC\s*(?P<dc>\d+)[^.]*\.\s*"
    rf"Failure:\s*(?:The\s+)?target has the (?P<condition>{_CONDITIONS}) condition "
    rf"until the (?P<edge>start|end) of (?P<owner>its|the [^.]+?[’']s) next turn",
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


def _timing(owner: str, edge: str) -> str:
    actor = "target" if owner.lower() == "its" else "source"
    return f"{actor}_turn_{edge.lower()}"


def _hit_save(text: str, maximum: CreatureSize | None) -> HitSavingThrowEffectDefinition | None:
    match = _SAVE_CONDITION.search(text) or _SAVE_FAILURE_CONDITION.search(text)
    if match is None:
        return None
    failure = ConditionEffectDefinition(
        condition=match.group("condition").lower(),
        max_target_size=maximum,
        expiry_timing=_timing(match.group("owner"), match.group("edge")),
    )
    return HitSavingThrowEffectDefinition(
        save_ability=match.group("ability").lower(), dc=int(match.group("dc")), failure_effects=[failure],
    )


def parse_attack_riders(text: str) -> list[object]:
    """Translate source hit-result sentences into source-neutral engine effects."""
    effects: list[object] = []
    maximum = _maximum(text)
    hit_save = _hit_save(text, maximum)
    failed_condition = None
    if hit_save is not None:
        effects.append(hit_save)
        failed_condition = hit_save.failure_effects[0].condition
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
        effects.append(GrappleEffectDefinition(escape_dc=int(grapple.group(1)), max_target_size=maximum))
    condition = _CONDITION.search(text)
    if condition and condition.group(1).lower() not in {"prone", failed_condition} and not grapple:
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

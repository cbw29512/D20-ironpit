from __future__ import annotations

import re

from app.content.monster_forced_movement_rider import parse_forced_movement_rider, strip_forced_movement_riders
from app.domain.actions import HitControlEffect
from app.domain.size import CreatureSize

_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"
_PRONE = re.compile(
    rf"(?:If the target is a (?P<size>{_SIZE}) or smaller creature, )?it has the Prone condition\.(?=\s|$)",
    re.I,
)
_GRAPPLE = re.compile(
    rf"If the target is a (?P<size>{_SIZE}) or smaller creature, it has the Grappled condition \(escape DC (?P<dc>\d+)\)(?: from [^.]+)?\.(?=\s|$)",
    re.I,
)
_RESTRAINED = re.compile(r"While Grappled, the target has the Restrained condition\.(?=\s|$)", re.I)
_POISONED = re.compile(
    r"(?:and )?the target has the Poisoned condition until the (?P<edge>start|end) of (?P<owner>its|the [A-Za-z’' -]+) next turn\.(?=\s|$)",
    re.I,
)
_CONTROL_WORDS = re.compile(
    r"\b(blinded|charmed|deafened|frightened|grappled|incapacitated|paralyzed|petrified|poisoned|prone|restrained|stunned|unconscious|push(?:es|ed)?|pull(?:s|ed)?|swallow(?:s|ed)?)\b",
    re.I,
)
_COMPLEX_REMAINDER = re.compile(
    r"\b(can't|cannot|only|total cover|suffocat|attach|detach|escape from|takes? .* damage at|damage at the)\b",
    re.I,
)


def _size(value: str | None) -> CreatureSize | None:
    return CreatureSize(value.lower()) if value else None


def _poison_timing(edge: str, owner: str) -> str:
    side = "source" if owner.lower().startswith("the ") else "target"
    return f"{side}_turn_{edge.lower()}"


def parse_simple_control_rider(hit: str) -> tuple[str, HitControlEffect | None, CreatureSize | None]:
    """Strip only exact source clauses already represented by universal on-hit mechanics."""
    text = hit
    control: HitControlEffect | None = None
    prone_size: CreatureSize | None = None

    grapple = _GRAPPLE.search(text)
    if grapple:
        restrains = bool(_RESTRAINED.search(text))
        control = HitControlEffect(
            max_target_size=_size(grapple.group("size")),
            grapple_escape_dc=int(grapple.group("dc")),
            restrains_while_grappled=restrains,
        )
        text = _GRAPPLE.sub("", text, count=1)
        if restrains:
            text = _RESTRAINED.sub("", text, count=1)

    poisoned = _POISONED.search(text)
    if poisoned and control is None:
        timing = _poison_timing(poisoned.group("edge"), poisoned.group("owner"))
        control = HitControlEffect(
            condition_id="poisoned",
            expires_at_start_of_source_turn=timing == "source_turn_start",
            expiry_timing=timing,
        )
        text = _POISONED.sub("", text, count=1)

    text, movement, movement_size = parse_forced_movement_rider(text)
    if movement is not None:
        if control is None:
            control = HitControlEffect(max_target_size=movement_size, forced_movement=movement)
        else:
            control = control.model_copy(update={
                "forced_movement": movement,
                "max_target_size": control.max_target_size or movement_size,
            })

    prone = _PRONE.search(text)
    if prone:
        prone_size = _size(prone.group("size")) or CreatureSize.GARGANTUAN
        text = _PRONE.sub("", text, count=1)

    return re.sub(r"\s+", " ", text).strip(" ,"), control, prone_size


def has_unmodeled_control_text(actions: str) -> bool:
    """Fail closed only for control clauses whose behavior remains after exact stripping."""
    if not _CONTROL_WORDS.search(actions):
        return False
    clean = strip_forced_movement_riders(actions)
    clean = _GRAPPLE.sub("", clean)
    clean = _RESTRAINED.sub("", clean)
    clean = _POISONED.sub("", clean)
    clean = _PRONE.sub("", clean)
    return bool(_CONTROL_WORDS.search(clean) or _COMPLEX_REMAINDER.search(clean))

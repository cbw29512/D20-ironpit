from __future__ import annotations

import re

from app.content.monster_forced_movement_rider import parse_forced_movement_rider
from app.content.monster_save_targeting import parse_save_targeting
from app.domain.actions import HitControlEffect, SavingThrowAction

_ABILITY = r"Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"
_SAVE_CONTROL = re.compile(
    rf"(?P<name>[A-Z][A-Za-z0-9 ’'()/-]+)\.\s+"
    rf"(?P<ability>{_ABILITY})\s+Saving Throw:\s*DC\s*(?P<dc>\d+),\s*(?P<target>[^.]+)\.\s+"
    r"Failure:\s*(?P<failure>The target is (?:pushed|pulled) .*?)(?="
    r"\s+[A-Z][A-Za-z0-9 ’'()/-]+\.\s+(?:(?:Melee|Ranged|Melee or Ranged) Attack Roll:|"
    rf"{_ABILITY} Saving Throw:)|$)",
    re.I | re.S,
)
_PRONE_REMAINDER = re.compile(r"^(?:,?\s*and\s+)?(?:(?:the target|it)\s+)?has the Prone condition\.\s*$", re.I)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _action(match: re.Match[str], monster_slug: str) -> SavingThrowAction:
    range_ft, area, target_size = parse_save_targeting(match.group("target"))
    clean, movement, movement_size = parse_forced_movement_rider(match.group("failure"))
    if movement is None:
        raise ValueError("save-control failure lacks supported forced movement")
    condition = None
    if clean:
        if not _PRONE_REMAINDER.fullmatch(clean):
            raise ValueError("save-control failure contains an unsupported rider")
        condition = "prone"
    control = HitControlEffect(
        max_target_size=movement_size or target_size,
        forced_movement=movement,
        condition_id=condition,
    )
    name = match.group("name").strip()
    return SavingThrowAction(
        id=f"srd-{monster_slug}-{_slug(name)}",
        name=name,
        save_ability=match.group("ability").lower(),
        dc=int(match.group("dc")),
        range_ft=range_ft,
        area=area,
        target_max_size=target_size,
        failure_control=control,
        animation="save-effect",
    )


def parse_simple_save_control_actions(row: dict[str, object]) -> list[SavingThrowAction]:
    try:
        monster_slug = _slug(str(row["name"]))
        return [_action(match, monster_slug) for match in _SAVE_CONTROL.finditer(str(row.get("actions", "")))]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"simple save-control parsing failed for {row.get('name', '<unknown>')}") from exc


def strip_simple_save_control_actions(actions: str) -> str:
    """Strip only save-control actions whose complete failure semantics compile safely."""
    clean = actions
    for match in sorted(list(_SAVE_CONTROL.finditer(actions)), key=lambda item: item.start(), reverse=True):
        try:
            _action(match, "audit")
        except ValueError:
            continue
        clean = clean[:match.start()] + " " + clean[match.end():]
    return clean

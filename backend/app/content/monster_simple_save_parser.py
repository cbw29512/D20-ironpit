from __future__ import annotations

import re

from app.content.monster_limited_use_source_audit import parse_action_recharges
from app.domain.actions import SavingThrowAction
from app.domain.areas import AreaTargeting

_DAMAGE_TYPES = r"Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder"
_ABILITY = r"Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"
_SAVE_DAMAGE = re.compile(
    rf"(?P<name>[A-Z][A-Za-z0-9 ’'()/-]+)\.\s+"
    rf"(?P<ability>{_ABILITY})\s+Saving Throw:\s*DC\s*(?P<dc>\d+),\s*(?P<target>[^.]+)\.\s+"
    rf"Failure:\s*\d+\s*\(\s*(?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\s*\)\s+"
    rf"(?P<type>{_DAMAGE_TYPES})\s+damage\.\s*(?P<success>Success:\s*Half damage\.)?",
    re.I,
)
_RECHARGE_SUFFIX = re.compile(r"\s*\(\s*Recharge\s+\d(?:\s*[-–]\s*\d)?\s*\)\s*$", re.I)
_CONE = re.compile(r"each (?:creature|enemy) in a (?P<length>\d+)-foot Cone$", re.I)
_LINE = re.compile(r"each (?:creature|enemy) in a (?P<length>\d+)-foot-long, (?P<width>\d+)-foot-wide Line$", re.I)
_EMANATION = re.compile(r"each (?:creature|enemy) in a (?P<radius>\d+)-foot Emanation originating from .+$", re.I)
_CYLINDER = re.compile(
    r"each (?:creature|enemy) in a (?P<radius>\d+)-foot-radius, (?P<height>\d+)-foot-high Cylinder "
    r"originating from a point .+ within (?P<range>\d+) feet$",
    re.I,
)
_SINGLE = re.compile(r"one creature .+ within (?P<range>\d+) feet$", re.I)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _targeting(text: str) -> tuple[int, AreaTargeting | None]:
    target = text.strip()
    match = _CONE.fullmatch(target)
    if match:
        length = int(match.group("length"))
        return length, AreaTargeting(shape="cone", length_ft=length)
    match = _LINE.fullmatch(target)
    if match:
        length, width = int(match.group("length")), int(match.group("width"))
        return length, AreaTargeting(shape="line", length_ft=length, width_ft=width)
    match = _EMANATION.fullmatch(target)
    if match:
        radius = int(match.group("radius"))
        return radius, AreaTargeting(shape="emanation", radius_ft=radius)
    match = _CYLINDER.fullmatch(target)
    if match:
        radius, height, origin_range = map(int, (match.group("radius"), match.group("height"), match.group("range")))
        return origin_range + radius, AreaTargeting(
            shape="cylinder", radius_ft=radius, height_ft=height, origin_range_ft=origin_range,
        )
    match = _SINGLE.fullmatch(target)
    if match:
        return int(match.group("range")), None
    raise ValueError(f"unsupported simple save target geometry: {target!r}")


def parse_simple_save_actions(row: dict[str, object]) -> list[SavingThrowAction]:
    actions = str(row.get("actions", ""))
    recharges = parse_action_recharges(row)
    monster_slug = _slug(str(row["name"]))
    parsed: list[SavingThrowAction] = []
    for match in _SAVE_DAMAGE.finditer(actions):
        printed = match.group("name").strip()
        name = _RECHARGE_SUFFIX.sub("", printed).strip()
        range_ft, area = _targeting(match.group("target"))
        bonus = int(match.group("bonus") or 0) * (-1 if match.group("sign") == "-" else 1)
        resource_id = f"srd-{monster_slug}-{_slug(name)}-recharge" if name in recharges else None
        parsed.append(SavingThrowAction(
            id=f"srd-{monster_slug}-{_slug(name)}",
            name=name,
            save_ability=match.group("ability").lower(),
            dc=int(match.group("dc")),
            range_ft=range_ft,
            area=area,
            damage_dice_count=int(match.group("count")),
            damage_dice_size=int(match.group("size")),
            damage_bonus=bonus,
            damage_type=match.group("type").lower(),
            success_damage="half" if match.group("success") else "none",
            resource_id=resource_id,
            animation="save-effect",
        ))
    return parsed


def strip_simple_save_actions(actions: str) -> str:
    """Remove only clauses that fully match the audited simple save/damage grammar."""
    clean = actions
    for match in reversed(list(_SAVE_DAMAGE.finditer(actions))):
        try:
            _targeting(match.group("target"))
        except ValueError:
            continue
        clean = clean[:match.start()] + " " + clean[match.end():]
    return clean

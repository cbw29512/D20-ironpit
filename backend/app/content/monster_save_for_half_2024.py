from __future__ import annotations

from collections import Counter
import logging
import re

from app.domain.actions import SavingThrowAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

_DAMAGE_TYPES = (
    "Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|"
    "Psychic|Radiant|Slashing|Thunder"
)
_SAVE_FOR_HALF = re.compile(
    rf"(?P<name>[A-Z][A-Za-z’' -]+?)"
    rf"(?:\s*\((?P<usage>Recharge\s+\d(?:-\d)?)\))?\.\s*"
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) "
    rf"Saving Throw:\s*DC\s*(?P<dc>\d+),\s*(?P<target>[^.]+)\.\s*"
    rf"Failure:\s*\d+\s*\(\s*(?P<count>\d+)d(?P<size>\d+)"
    rf"(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\s*\)\s*"
    rf"(?P<dtype>{_DAMAGE_TYPES}) damage\.\s*Success:\s*Half damage\.",
    re.I,
)
_LINE = re.compile(r"(?P<length>\d+)-foot-long,\s*(?P<width>\d+)-foot-wide Line", re.I)
_CONE = re.compile(r"(?P<length>\d+)-foot Cone", re.I)
_SPHERE = re.compile(
    r"(?P<radius>\d+)-foot-radius Sphere centered on a point .*? within (?P<range>\d+) feet",
    re.I,
)
_WITHIN = re.compile(r"within (?P<range>\d+) feet", re.I)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _targeting(target: str) -> tuple[int, AreaTargeting | None]:
    line = _LINE.search(target)
    if line:
        length = int(line.group("length"))
        return length, AreaTargeting(
            shape="line", origin="self", length_ft=length, width_ft=int(line.group("width")),
        )
    cone = _CONE.search(target)
    if cone:
        length = int(cone.group("length"))
        return length, AreaTargeting(shape="cone", origin="self", length_ft=length)
    sphere = _SPHERE.search(target)
    if sphere:
        return int(sphere.group("range")), AreaTargeting(
            shape="radius", origin="point", radius_ft=int(sphere.group("radius")),
        )
    within = _WITHIN.search(target)
    if within:
        return int(within.group("range")), None
    raise ValueError(f"Unsupported save-for-half target geometry: {target!r}")


def compile_save_for_half_actions(row: dict[str, object]) -> list[SavingThrowAction]:
    """Compile source actions whose entire save outcome is typed damage / half damage."""
    try:
        monster_name = str(row["name"])
        actions = str(row.get("actions", ""))
        compiled: list[SavingThrowAction] = []
        for match in _SAVE_FOR_HALF.finditer(actions):
            name = match.group("name").strip()
            target = match.group("target")
            if re.search(r"\\bGrappled by the\\b", target, re.I):
                continue
            range_ft, area = _targeting(target)
            bonus = int(match.group("bonus") or 0)
            if match.group("sign") == "-":
                bonus = -bonus
            usage = match.group("usage")
            compiled.append(SavingThrowAction(
                id=f"srd-{_slug(monster_name)}-{_slug(name)}",
                name=name,
                save_ability=match.group("ability").lower(),
                dc=int(match.group("dc")),
                range_ft=range_ft,
                area=area,
                damage_dice_count=int(match.group("count")),
                damage_dice_size=int(match.group("size")),
                damage_bonus=bonus,
                damage_type=match.group("dtype").lower(),
                success_damage="half",
                resource_id=_slug(name) if usage else None,
            ))
        return compiled
    except (KeyError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Failed to compile save-for-half actions for %s.", row.get("name", "<unknown>"))
        raise RuntimeError("Monster save-for-half source compilation failed.") from exc


def compiled_save_signatures(row: dict[str, object]) -> Counter[tuple[str, int]]:
    try:
        return Counter((action.save_ability, action.dc) for action in compile_save_for_half_actions(row))
    except Exception:
        logger.exception("Failed to summarize save-for-half signatures for %s.", row.get("name", "<unknown>"))
        raise

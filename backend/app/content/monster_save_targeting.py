from __future__ import annotations

import re

from app.domain.areas import AreaTargeting
from app.domain.size import CreatureSize

_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"
_CONE = re.compile(r"each (?:creature|enemy) in a (?P<length>\d+)-foot Cone$", re.I)
_LINE = re.compile(r"each (?:creature|enemy) in a (?P<length>\d+)-foot-long, (?P<width>\d+)-foot-wide Line$", re.I)
_EMANATION = re.compile(r"each (?:creature|enemy) in a (?P<radius>\d+)-foot Emanation originating from .+$", re.I)
_CYLINDER = re.compile(
    r"each (?:creature|enemy) in a (?P<radius>\d+)-foot-radius, (?P<height>\d+)-foot-high Cylinder "
    r"originating from a point .+ within (?P<range>\d+) feet$",
    re.I,
)
_SINGLE = re.compile(rf"one (?:(?P<size>{_SIZE}) or smaller )?creature .+ within (?P<range>\d+) feet$", re.I)


def parse_save_targeting(text: str) -> tuple[int, AreaTargeting | None, CreatureSize | None]:
    """Compile exact SRD target geometry into universal range/area data."""
    try:
        target = text.strip()
        match = _CONE.fullmatch(target)
        if match:
            length = int(match.group("length"))
            return length, AreaTargeting(shape="cone", length_ft=length), None
        match = _LINE.fullmatch(target)
        if match:
            length, width = int(match.group("length")), int(match.group("width"))
            return length, AreaTargeting(shape="line", length_ft=length, width_ft=width), None
        match = _EMANATION.fullmatch(target)
        if match:
            radius = int(match.group("radius"))
            return radius, AreaTargeting(shape="emanation", radius_ft=radius), None
        match = _CYLINDER.fullmatch(target)
        if match:
            radius = int(match.group("radius")); height = int(match.group("height")); origin_range = int(match.group("range"))
            return origin_range + radius, AreaTargeting(
                shape="cylinder", radius_ft=radius, height_ft=height, origin_range_ft=origin_range,
            ), None
        match = _SINGLE.fullmatch(target)
        if match:
            size = CreatureSize(match.group("size").lower()) if match.group("size") else None
            return int(match.group("range")), None, size
        raise ValueError(f"unsupported simple save target geometry: {target!r}")
    except (TypeError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("unsupported simple save target geometry"):
            raise
        raise ValueError("save target geometry parsing failed") from exc

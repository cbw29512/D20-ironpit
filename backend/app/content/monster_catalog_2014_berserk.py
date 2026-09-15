from __future__ import annotations

import html
import re

from app.domain.berserk import BerserkProfile

_BERSERK = re.compile(
    r"Berserk\.\s*Whenever the [^.]+ starts its turn with (?P<hp>\d+) hit points or fewer, "
    r"roll a d(?P<die>\d+)\.\s*On a (?P<trigger>\d+), the [^.]+ goes berserk\.",
    re.I,
)


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def berserk_profile_2014(source_traits: str | None) -> BerserkProfile | None:
    match = _BERSERK.search(_plain(source_traits))
    if match is None:
        return None
    return BerserkProfile(
        hp_threshold=int(match.group("hp")),
        die_size=int(match.group("die")),
        trigger_roll=int(match.group("trigger")),
    )

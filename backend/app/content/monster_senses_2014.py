"""2014 SRD source-derived sight ranges; never use monster-name dispatch."""
from __future__ import annotations
import re
from app.content.monster_source_2014 import SourceMonster2014

def special_senses_2014(monster: SourceMonster2014) -> tuple[int, int]:
    """Bind only complete, unconditional Blindsight/Truesight range semantics."""
    source = monster.senses
    if not isinstance(source, str):
        raise ValueError("2014 monster special senses must be source text.")
    ranges: list[int] = []
    for name in ("blindsight", "truesight"):
        found = re.findall(rf"\b{name}\b", source, re.I)
        matches = re.findall(rf"\b{name}\s+(\d+)\s*ft\.", source, re.I)
        if len(found) != len(matches) or len(matches) > 1:
            raise ValueError(f"Unsupported {name} source syntax for {monster.id}.")
        amount = int(matches[0]) if matches else 0
        if amount > 1000:
            raise ValueError(f"Out-of-bounds {name} range for {monster.id}.")
        # Unmodeled blind-beyond-radius means this is NOT the same semantic
        # capability as normal unrestricted sight with a blindsight range.
        # Do not grant this special-case a silently broadened sight profile.
        if name == "blindsight" and re.search(
            r"\bblind\s+beyond\s+this\s+radius\b", source, re.I,
        ):
            amount = 0
        ranges.append(amount)
    return ranges[0], ranges[1]

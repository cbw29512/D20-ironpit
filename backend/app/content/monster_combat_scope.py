from __future__ import annotations

import re

_SPACE = re.compile(r"\s+")
_ANNOTATION = re.compile(r"\s*\([^)]*\)\s*$")
_POST_COMBAT_LYCANTHROPY = re.compile(
    r"If the target is a Humanoid, it is subjected to the following effect\. "
    r"Constitution Saving Throw: DC \d+\. Failure: The target is cursed\. "
    r"If the cursed target drops to 0 Hit Points, it instead becomes a [A-Za-z-]+ under the GM[’']s control and has 10 Hit Points\. "
    r"Success: The target is immune to this [A-Za-z-]+[’']s curse for 24 hours\.",
    re.I,
)
_POST_COMBAT_CORPSE_CREATION = re.compile(
    r"\b[A-Z][A-Za-z’'\- ]+\. The [A-Za-z’'\- ]+ targets? a Humanoid corpse [^.]*\. "
    r"The target[’']s spirit rises as a [A-Za-z’'\-]+ [^.]*\. "
    r"The [A-Za-z’'\-]+ is under the [^.]+ control\. The [^.]+ can have no more than [^.]+\. ?",
)
_BATTLE_READY_HYBRID = re.compile(
    r"\bshape-shifts into a (?P<size>Tiny|Small|Medium|Large|Huge|Gargantuan) [^.]*?hybrid(?: form)?\b",
    re.I,
)
_NON_PROVOKING_MOVEMENT = re.compile(
    r"\b(?:without provoking Opportunity Attacks?|(?:doesn[’']t|does not) provoke an Opportunity Attack)\b",
    re.I,
)

# Iron Pit scope is intentionally narrower than the full tabletop ruleset.
# Movement, positioning, senses, stealth, environment, and narrative-only text
# do not block certification unless the same feature also changes combat math
# or meaningful action economy.
_COMBAT_MATH = (
    re.compile(r"\bdamage\b", re.I),
    re.compile(r"\bHit Points?\b|\bTemporary Hit Points?\b", re.I),
    re.compile(r"\bAC\b|\bArmor Class\b", re.I),
    re.compile(r"\battack roll(?:s)?\b|\bdamage roll(?:s)?\b|\bto hit\b", re.I),
    re.compile(r"\battacks?\b", re.I),
    re.compile(r"\bsaving throw(?:s)?\b|\bsave DC\b|\bD20 Test(?:s)?\b", re.I),
    re.compile(r"\binitiative\b|\bcritical hit(?:s)?\b|\bConcentration\b", re.I),
    re.compile(
        r"\b(?:blinded|charmed|frightened|grappled|incapacitated|paralyzed|petrified|poisoned|prone|restrained|stunned|unconscious)\b",
        re.I,
    ),
    re.compile(r"\b(?:heavily obscured|invisible|invisibility)\b", re.I),
    re.compile(
        r"\b(?:can't|cannot)\s+(?:take|use)\s+(?:an?\s+)?(?:Action|Bonus Action|Reaction)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:takes?|gains?|uses?)\s+(?:an?\s+)?(?:additional|extra)\s+(?:Action|Bonus Action|Reaction)\b",
        re.I,
    ),
    re.compile(r"\bmakes?\s+(?:one|two|three|four|an?)\b[^.]{0,70}\battack\b", re.I),
    re.compile(r"\bcasts?\b", re.I),
    re.compile(
        r"\b(?:add(?:s)?|subtract(?:s)?)\s+[+-]?\d+\s+(?:to|from)\s+(?:the|that|its|their)?\s*roll\b",
        re.I,
    ),
    re.compile(
        r"\b(?:Advantage|Disadvantage)\b[^.]{0,90}\b(?:attack|saving throw|D20 Test)\b"
        r"|\b(?:attack|saving throw|D20 Test)\b[^.]{0,90}\b(?:Advantage|Disadvantage)\b",
        re.I,
    ),
)


def normalized_source_text(value: object) -> str:
    return _SPACE.sub(" ", str(value or "")).strip()


def strip_post_combat_outcomes(value: object) -> str:
    """Remove source consequences that cannot change the winner of the current standard Iron Pit battle."""
    text = _POST_COMBAT_LYCANTHROPY.sub("", normalized_source_text(value))
    return _POST_COMBAT_CORPSE_CREATION.sub("", text).strip()


def battle_ready_size(row: dict[str, object]) -> str | None:
    """Resolve an at-will hybrid form used on arena entry when only form presentation/size differs."""
    match = _BATTLE_READY_HYBRID.search(normalized_source_text(row.get("bonusActions", "")))
    return match.group("size").lower() if match else None


def base_feature_name(name: str) -> str:
    return _ANNOTATION.sub("", normalized_source_text(name)).strip()


def _heading_start(text: str, marker: str) -> int:
    """Find a reviewed heading at a sentence boundary, not an earlier prose reference."""
    start = text.find(marker)
    while start >= 0:
        if start == 0 or text[start - 2:start] == ". ":
            return start
        start = text.find(marker, start + 1)
    return -1


def feature_blocks(source: object, headings: list[str] | tuple[str, ...]) -> dict[str, str]:
    """Split a reviewed SRD section by actual heading occurrences without guessing new headings."""
    text = normalized_source_text(source)
    if not text:
        return {}
    located: list[tuple[int, int, str]] = []
    for heading in headings:
        marker = f"{normalized_source_text(heading)}."
        start = _heading_start(text, marker)
        if start < 0:
            raise ValueError(f"SRD feature heading {heading!r} was not found in source section.")
        located.append((start, start + len(marker), heading))
    located.sort(key=lambda item: item[0])
    blocks: dict[str, str] = {}
    for index, (start, _, heading) in enumerate(located):
        end = located[index + 1][0] if index + 1 < len(located) else len(text)
        blocks[heading] = text[start:end].strip()
    return blocks


def combat_math_relevant(source: object) -> bool:
    """Return True only when source text can change an Iron Pit combat outcome."""
    text = strip_post_combat_outcomes(source)
    if not text:
        return False
    # Non-provoking movement remains movement-only in fixed Pit formation; strip
    # only the negated Opportunity Attack phrase so real attack rules still count.
    text = _NON_PROVOKING_MOVEMENT.sub("", text)
    return any(pattern.search(text) for pattern in _COMBAT_MATH)


def arena_neutral_features(source: object, headings: list[str] | tuple[str, ...]) -> set[str]:
    blocks = feature_blocks(source, headings)
    return {heading for heading, block in blocks.items() if not combat_math_relevant(block)}

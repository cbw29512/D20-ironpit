from __future__ import annotations

import re

_DIRECT_CONDITIONS = (
    "blinded", "charmed", "frightened", "incapacitated", "invisible", "paralyzed",
    "petrified", "poisoned", "prone", "restrained", "stunned", "unconscious", "exhaustion",
)
_CONDITION_RE = re.compile(r"\b(?:" + "|".join(_DIRECT_CONDITIONS) + r")\b", re.I)
_ATTACK_ROLL_RE = re.compile(r"\b(?:melee|ranged|melee or ranged)\s+attack roll\b|\bnext attack roll\b", re.I)
_SAVE_MATH_RE = re.compile(
    r"\b(?:advantage|disadvantage)\b[^.]{0,80}\bsaving throws?\b|"
    r"\bsaving throws?\b[^.]{0,80}\b(?:advantage|disadvantage)\b|"
    r"\bfails?\s+(?:a|the)\s+saving throw\b[^.]{0,80}\b(?:succeed|success)\b",
    re.I,
)
_ATTACK_MATH_RE = re.compile(
    r"\b(?:advantage|disadvantage)\b[^.]{0,80}\battack rolls?\b|"
    r"\battack rolls?\b[^.]{0,80}\b(?:advantage|disadvantage)\b",
    re.I,
)
_INITIATIVE_RE = re.compile(r"\b(?:advantage|disadvantage)\b[^.]{0,80}\binitiative\b|\binitiative\b[^.]{0,80}\b(?:advantage|disadvantage)\b", re.I)
_DAMAGE_RE = re.compile(r"\bdamage\b|\bdamage rolls?\b", re.I)
_HP_RE = re.compile(r"\bhit points?\b|\btemporary hit points?\b|\bhit point maximum\b", re.I)
_AC_RE = re.compile(r"\barmor class\b|\bAC\s*[+-]?\s*\d+\b|\badds?\s+\d+\s+to\s+(?:its|the target['’]s)\s+AC\b", re.I)
_ACTION_ECONOMY_RE = re.compile(
    r"\b(?:can(?:not|'t|’t)|doesn['’]t)\s+(?:take|use|make)\s+(?:an?\s+)?(?:action|bonus action|reaction|attack)\b|"
    r"\btakes?\s+no\s+(?:action|bonus action|reaction)\b|"
    r"\b(?:extra|additional)\s+(?:action|bonus action|reaction|attack)\b|"
    r"\bmakes?\s+(?:one|two|three|four|five|six|\d+)\s+[^.]{0,40}\battacks?\b|"
    r"\bcan(?:not|'t|’t)\s+cast\s+spells?\b",
    re.I,
)
_TARGETING_RE = re.compile(
    r"\bcan(?:not|'t|’t)\s+be\s+targeted\b|\btotal cover\b|\bheavily obscured\b|"
    r"\bone creature grappled by\b|\beach creature grappled by\b",
    re.I,
)
_CRITICAL_RE = re.compile(r"\bcritical hits?\b", re.I)
_DEATH_RE = re.compile(r"\bdies?\b|\bdeath saving throws?\b|\bstable\b|\breduced to 0 hit points?\b|\bsuffocat", re.I)
_CONCENTRATION_RE = re.compile(r"\bconcentration\b", re.I)
_SUMMON_RE = re.compile(r"\b(?:summons?|creates?)\b[^.]{0,100}\b(?:creature|monster|specter|zombie|skeleton)\b", re.I)
_ABILITY_SCORE_RE = re.compile(r"\b(?:strength|dexterity|constitution|intelligence|wisdom|charisma)\s+score\s+(?:decreases|increases)\b", re.I)
_MOVEMENT_ONLY_RE = re.compile(
    r"\b(?:speed|walk|climb|fly|swim|burrow|hover|jump|leap|teleport(?:s|ed|ing)?|difficult terrain|"
    r"push(?:es|ed)?|pull(?:s|ed)?|grappled|disengage|dash|move(?:s|d)?|movement|space)\b",
    re.I,
)
_CONNECTORS = frozenset({"a", "an", "and", "of", "or", "the", "to"})


def _is_heading(value: str) -> bool:
    if not value or len(value) > 100 or any(mark in value for mark in ",:;!?"):
        return False
    plain = re.sub(r"\s*\([^)]*\)$", "", value).strip()
    words = plain.split()
    return bool(words) and all(word.lower() in _CONNECTORS or re.fullmatch(r"[A-Z][A-Za-z0-9’'\-]*", word) for word in words)


def source_feature_blocks(source: object) -> list[tuple[str, str]]:
    text = re.sub(r"\s+", " ", str(source or "")).strip()
    if not text:
        return []
    blocks: list[tuple[str, str]] = []
    name: str | None = None
    parts: list[str] = []
    for sentence in re.split(r"(?<=\.)\s+", text):
        candidate = sentence[:-1].strip() if sentence.endswith(".") else ""
        if _is_heading(candidate):
            if name is not None:
                blocks.append((name, " ".join(parts)))
            name, parts = candidate, [sentence]
        elif name is not None:
            parts.append(sentence)
    if name is not None:
        blocks.append((name, " ".join(parts)))
    return blocks


def feature_block(source: object, heading: str) -> str:
    return next((block for name, block in source_feature_blocks(source) if name == heading), "")


def direct_combat_math_reasons(text: object) -> frozenset[str]:
    source = str(text or "").strip()
    if not source:
        return frozenset()
    checks = (
        ("attack-roll", _ATTACK_ROLL_RE), ("attack-math", _ATTACK_MATH_RE), ("save-math", _SAVE_MATH_RE),
        ("initiative", _INITIATIVE_RE), ("damage", _DAMAGE_RE), ("hp", _HP_RE), ("armor-class", _AC_RE),
        ("condition", _CONDITION_RE), ("action-economy", _ACTION_ECONOMY_RE), ("targeting", _TARGETING_RE),
        ("critical", _CRITICAL_RE), ("death", _DEATH_RE), ("concentration", _CONCENTRATION_RE),
        ("summon", _SUMMON_RE), ("ability-score", _ABILITY_SCORE_RE),
    )
    return frozenset(reason for reason, pattern in checks if pattern.search(source))


def affects_mvp_combat_math(text: object) -> bool:
    return bool(direct_combat_math_reasons(text))


def movement_only_for_mvp(text: object) -> bool:
    source = str(text or "").strip()
    return bool(source and _MOVEMENT_ONLY_RE.search(source) and not affects_mvp_combat_math(source))

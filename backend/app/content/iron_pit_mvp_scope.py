from __future__ import annotations

import re

# Iron Pit MVP models only effects that can directly change the mathematical
# outcome of the current fight. Pure movement/exploration/flavor semantics are
# deferred and must not block monster or hero certification.

_DIRECT_CONDITIONS = (
    "blinded", "charmed", "frightened", "incapacitated", "invisible",
    "paralyzed", "petrified", "poisoned", "prone", "restrained", "stunned",
    "unconscious", "exhaustion",
)
_CONDITION_RE = re.compile(r"\b(?:" + "|".join(_DIRECT_CONDITIONS) + r")\b", re.I)
_ATTACK_ROLL_RE = re.compile(r"\b(?:melee|ranged|melee or ranged)\s+attack roll\b|\bnext attack roll\b", re.I)
_SAVE_MATH_RE = re.compile(r"\b(?:advantage|disadvantage)\b[^.]{0,80}\bsaving throws?\b|\bsaving throws?\b[^.]{0,80}\b(?:advantage|disadvantage)\b", re.I)
_ATTACK_MATH_RE = re.compile(r"\b(?:advantage|disadvantage)\b[^.]{0,80}\battack rolls?\b|\battack rolls?\b[^.]{0,80}\b(?:advantage|disadvantage)\b", re.I)
_INITIATIVE_RE = re.compile(r"\b(?:advantage|disadvantage)\b[^.]{0,80}\binitiative\b|\binitiative\b[^.]{0,80}\b(?:advantage|disadvantage)\b", re.I)
_DAMAGE_RE = re.compile(r"\bdamage\b|\bdamage rolls?\b", re.I)
_HP_RE = re.compile(r"\bhit points?\b|\btemporary hit points?\b|\bhit point maximum\b|\bregains?\b[^.]{0,50}\bhit points?\b", re.I)
_AC_RE = re.compile(r"\barmor class\b|\bAC\s*[+-]?\s*\d+\b|\badds?\s+\d+\s+to\s+(?:its|the target['’]s)\s+AC\b", re.I)
_ACTION_ECONOMY_RE = re.compile(
    r"\b(?:can(?:not|'t)|doesn['’]t)\s+(?:take|use)\s+(?:an?\s+)?(?:action|bonus action|reaction)\b"
    r"|\b(?:extra|additional)\s+(?:action|bonus action|reaction|attack)\b"
    r"|\bmakes?\s+(?:one|two|three|four|five|six|\d+)\s+[^.]{0,40}\battacks?\b",
    re.I,
)
_TARGETING_RE = re.compile(
    r"\bcan(?:not|'t)\s+be\s+targeted\b|\btotal cover\b|\btarget has cover\b"
    r"|\bone creature grappled by\b|\beach creature grappled by\b",
    re.I,
)
_CRITICAL_RE = re.compile(r"\bcritical hit\b|\bcritical hits?\b", re.I)
_DEATH_RE = re.compile(r"\bdies?\b|\bdeath saving throws?\b|\bstable\b|\breduced to 0 hit points?\b", re.I)
_CONCENTRATION_RE = re.compile(r"\bconcentration\b", re.I)
_SUMMON_RE = re.compile(r"\b(?:summons?|creates?)\b[^.]{0,100}\b(?:creature|monster|specter|zombie|skeleton)\b", re.I)
_MOVEMENT_ONLY_RE = re.compile(
    r"\b(?:speed|walk|climb|fly|swim|burrow|hover|jump|leap|teleport|difficult terrain|"
    r"push(?:es|ed)?|pull(?:s|ed)?|grappled|disengage|dash|move(?:s|d)?|movement|space)\b",
    re.I,
)


def direct_combat_math_reasons(text: object) -> frozenset[str]:
    """Return MVP outcome categories present in source text.

    A saving throw by itself is not a reason: its failure/success consequence must
    contain an outcome-changing effect. Grappled/push/pull/Speed are likewise not
    reasons unless another direct-math rule depends on them.
    """
    source = str(text or "").strip()
    if not source:
        return frozenset()
    reasons: set[str] = set()
    checks = (
        ("attack-roll", _ATTACK_ROLL_RE), ("attack-math", _ATTACK_MATH_RE),
        ("save-math", _SAVE_MATH_RE), ("initiative", _INITIATIVE_RE),
        ("damage", _DAMAGE_RE), ("hp", _HP_RE), ("armor-class", _AC_RE),
        ("condition", _CONDITION_RE), ("action-economy", _ACTION_ECONOMY_RE),
        ("targeting", _TARGETING_RE), ("critical", _CRITICAL_RE),
        ("death", _DEATH_RE), ("concentration", _CONCENTRATION_RE),
        ("summon", _SUMMON_RE),
    )
    for reason, pattern in checks:
        if pattern.search(source):
            reasons.add(reason)
    return frozenset(reasons)


def affects_mvp_combat_math(text: object) -> bool:
    return bool(direct_combat_math_reasons(text))


def movement_only_for_mvp(text: object) -> bool:
    source = str(text or "").strip()
    return bool(source and _MOVEMENT_ONLY_RE.search(source) and not affects_mvp_combat_math(source))

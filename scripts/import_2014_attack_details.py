from __future__ import annotations

import re

DAMAGE_TYPES = {
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
}
_ROLLED = re.compile(
    r"(?:,?\s*(?:plus|and)\s+)(\d+)\s*\((\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\)\s*([A-Za-z]+) damage",
    re.I,
)
_FIXED = re.compile(r"(?:,?\s*(?:plus|and)\s+)(\d+)\s+([A-Za-z]+) damage", re.I)
_PRONE_SAVE = re.compile(
    r"(?:If (?:the )?target is (?:(?:(Tiny|Small|Medium|Large|Huge) or smaller)|a creature),?\s*)?"
    r"(?:the target|it) must succeed on a DC (\d+) (Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw or be knocked prone\.?'?",
    re.I,
)
_GRAPPLE = re.compile(
    r"(?:If (?:the )?target is (?:a )?(?:(Tiny|Small|Medium|Large|Huge) or smaller)(?: creature)?,?\s*)?"
    r"(?:the target|it) is grappled \(escape DC (\d+)\)",
    re.I,
)
_RESTRAINED = re.compile(
    r"Until (?:this|the) grapple ends,?\s*(?:the target|it) is restrained",
    re.I,
)
_NO_REPEAT_TARGET = re.compile(
    r"(?:and\s+)?(?:the\s+)?[A-Za-z' -]+ can(?:not|'t) (?:use this attack on|bite|attack|constrict|grapple) another target",
    re.I,
)


def _rolled(match: re.Match[str]) -> dict | None:
    average, count, size, sign, bonus, damage_type = match.groups()
    damage_type = damage_type.lower()
    if damage_type not in DAMAGE_TYPES: return None
    return {"average": int(average), "dice_count": int(count), "dice_size": int(size),
            "bonus": int(bonus or 0) * (-1 if sign == "-" else 1), "type": damage_type}


def _fixed(match: re.Match[str]) -> dict | None:
    amount, damage_type = match.groups(); damage_type = damage_type.lower()
    if damage_type not in DAMAGE_TYPES: return None
    return {"average": int(amount), "dice_count": 0, "dice_size": 6, "bonus": int(amount), "type": damage_type}


def parse_secondary_damage(remainder: str) -> tuple[list[dict], str]:
    extras: list[dict] = []
    def replace_rolled(match: re.Match[str]) -> str:
        parsed = _rolled(match)
        if parsed is None: return match.group(0)
        extras.append(parsed); return " "
    def replace_fixed(match: re.Match[str]) -> str:
        parsed = _fixed(match)
        if parsed is None: return match.group(0)
        extras.append(parsed); return " "
    residual = _ROLLED.sub(replace_rolled, remainder); residual = _FIXED.sub(replace_fixed, residual)
    residual = re.sub(r"^[\s,;]*(?:and\s+)?|[\s,;]+$", "", residual, flags=re.I)
    return extras, residual.strip(" .")


def parse_on_hit_save_condition(remainder: str) -> tuple[dict | None, str]:
    match = _PRONE_SAVE.search(remainder)
    if not match: return None, remainder
    max_size, dc, ability = match.groups()
    effect = {"save_ability": ability.lower(), "dc": int(dc), "condition_id": "prone",
              "max_target_size": max_size.lower() if max_size else None}
    residual = (remainder[:match.start()] + " " + remainder[match.end():]).strip(" .,;")
    return effect, residual


def parse_on_hit_control(remainder: str) -> tuple[dict | None, bool, str]:
    match = _GRAPPLE.search(remainder)
    if not match: return None, False, remainder
    max_size, dc = match.groups(); before = remainder[:match.start()]; after = remainder[match.end():]
    restrains = bool(_RESTRAINED.search(after)); after = _RESTRAINED.sub(" ", after, count=1)
    forbid = bool(_NO_REPEAT_TARGET.search(after)); after = _NO_REPEAT_TARGET.sub(" ", after, count=1)
    control = {"grapple_escape_dc": int(dc), "restrains_while_grappled": restrains}
    if max_size: control["max_target_size"] = max_size.lower()
    residual = re.sub(r"^[\s,;]*(?:and\s+)?|[\s,;]+$", "", f"{before} {after}", flags=re.I).strip(" .")
    return control, forbid, residual

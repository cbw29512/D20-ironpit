from __future__ import annotations

import re

DAMAGE_TYPES = {
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
}
_ROLLED = re.compile(r"(?:,?\s*(?:plus|and)\s+)(\d+)\s*\((\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\)\s*([A-Za-z]+) damage", re.I)
_FIXED = re.compile(r"(?:,?\s*(?:plus|and)\s+)(\d+)\s+([A-Za-z]+) damage", re.I)
_PRONE_SAVE = re.compile(r"(?:If (?:the )?target is (?:(?:(Tiny|Small|Medium|Large|Huge) or smaller)|a creature),?\s*)?(?:the target|it) must succeed on a DC (\d+) (Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw or be knocked prone\.?'?", re.I)
_TIMED_REPEAT_CONDITION = re.compile(r"(?:If (?:the )?target is a creature,?\s*)?(?:the target|it) must succeed on a DC (\d+) (Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw or (?:be|become) (poisoned|paralyzed) for 1 minute\.\s*(?:The (?:target|creature)|It) can repeat the saving throw at the end of each of its turns,? ending the effect on itself on a success\.?'?", re.I)
_DISEASE_POISON = re.compile(r"(?:If (?:the )?target is a creature,?\s*)?(?:the target|it) must succeed on a DC (\d+) Constitution saving throw against disease or become poisoned until the disease is cured\.?'?", re.I)
_SAVE_DAMAGE_HALF = re.compile(r"(?:the target|it) must make a DC (\d+) (Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw,? taking \d+ \((\d+)d(\d+)(?:\s*([+\-−])\s*(\d+))?\) ([A-Za-z]+) damage on a failed save,? or half as much damage on a successful one\.?'?", re.I)
_SAVE_DAMAGE_NONE = re.compile(r"(?:the target|it) must succeed on a DC (\d+) (Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw or take \d+ \((\d+)d(\d+)(?:\s*([+\-−])\s*(\d+))?\) ([A-Za-z]+) damage\.?'?", re.I)
_ZERO_HP_STABLE = re.compile(r"If the ([A-Za-z]+) damage reduces the target to 0 hit points, the target is stable but ([A-Za-z]+) for (\d+) (hour|hours|minute|minutes), even after regaining hit points, and is ([A-Za-z]+) while \2 in this way", re.I)
_GRAPPLE = re.compile(r"(?:If (?:the )?target is (?:a )?(?:(Tiny|Small|Medium|Large|Huge) or smaller)(?: creature)?,?\s*)?(?:the target|it) is grappled \(escape DC (\d+)\)", re.I)
_RESTRAINED = re.compile(r"(?:Until (?:this|the) grapple ends,?\s*(?:the target|the creature|it) is restrained|(?:the target|the creature|it) is restrained until (?:this|the) grapple ends)", re.I)
_NO_REPEAT_TARGET = re.compile(r"(?:and\s+)?(?:the\s+)?[A-Za-z' -]+ can(?:not|'t) (?:use this attack on|bite|attack|constrict|grapple) another target", re.I)
_OWN_ATTACK_TARGET = re.compile(r"(?:and\s+)?(?:the\s+)?[A-Za-z' -]+ can(?:not|'t) use its [A-Za-z' -]+ on another target", re.I)
_PER_LIMB_GRAPPLE = re.compile(r"The [A-Za-z' -]+ has two [A-Za-z' -]+, each of which can grapple only one target", re.I)
_ALREADY_CONTROLLING = re.compile(r"(?:if\s+)?(?:the\s+)?[A-Za-z' -]+ (?:isn't|is not) already (?:constricting|grappling) a creature,?\s*(?:and\s+)?", re.I)
_UNATTENDED_OBJECT_ONLY = re.compile(r"If the target is a flammable object that isn't being worn or carried, it also catches fire", re.I)
_POST_KILL_ONLY = re.compile(r"If the target is killed by this damage, it is absorbed into the mouther", re.I)
_LYCANTHROPY_ONLY = re.compile(r"If the target is a humanoid, it must succeed on a DC \d+ Constitution saving throw or be cursed with (?:werebear|wererat|weretiger|werewolf) lycanthropy", re.I)
_REST_ONLY_CURSE = re.compile(r"the target is cursed if it is a creature\. The magical curse takes effect whenever the target takes a short or long rest, filling the target's thoughts with horrible images and dreams\. The cursed target gains no benefit from finishing a short or long rest", re.I)
_DISEASE_LONG_TERM = re.compile(r"Every 24 hours that elapse,.*?(?:dies if the disease reduces its hit point maximum to 0\.?|until the disease is cured\.?)", re.I | re.S)
_DISEASE_DEATH_ONLY = re.compile(r"The creature dies if the disease reduces its hit point maximum to 0", re.I)
_DISEASE_REDUCTION_DURATION_ONLY = re.compile(r"This reduction to the target's hit point maximum lasts until the disease is cured", re.I)
_REST_CURSE_DURATION_ONLY = re.compile(r"The curse lasts until it is lifted by a remove curse spell or similar magic", re.I)


def strip_noncombat_attack_residual(remainder: str) -> str:
    cleaned = remainder
    for pattern in (
        _UNATTENDED_OBJECT_ONLY, _POST_KILL_ONLY, _LYCANTHROPY_ONLY, _REST_ONLY_CURSE,
        _DISEASE_LONG_TERM, _DISEASE_DEATH_ONLY, _DISEASE_REDUCTION_DURATION_ONLY,
        _REST_CURSE_DURATION_ONLY,
    ):
        cleaned = pattern.sub(" ", cleaned)
    return cleaned.strip(" .,;")


def _rolled(match: re.Match[str]) -> dict | None:
    average, count, size, sign, bonus, damage_type = match.groups(); damage_type = damage_type.lower()
    if damage_type not in DAMAGE_TYPES: return None
    return {"average": int(average), "dice_count": int(count), "dice_size": int(size), "bonus": int(bonus or 0) * (-1 if sign == "-" else 1), "type": damage_type}


def _fixed(match: re.Match[str]) -> dict | None:
    amount, damage_type = match.groups(); damage_type = damage_type.lower()
    if damage_type not in DAMAGE_TYPES: return None
    return {"average": int(amount), "dice_count": 0, "dice_size": 6, "bonus": int(amount), "type": damage_type}


def _save_damage_effect(match: re.Match[str], success_damage: str) -> dict | None:
    dc, ability, count, size, sign, bonus, damage_type = match.groups(); dtype = damage_type.lower()
    if dtype not in DAMAGE_TYPES: return None
    modifier = int(bonus or 0) * (-1 if sign in {"-", "−"} else 1)
    return {"save_ability": ability.lower(), "dc": int(dc), "damage_dice_count": int(count), "damage_dice_size": int(size), "damage_bonus": modifier, "damage_type": dtype, "success_damage": success_damage}


def _zero_hp_rider(effect: dict, residual: str) -> tuple[dict, str]:
    match = _ZERO_HP_STABLE.search(residual)
    if match is None: return effect, residual
    damage_type, first, amount, unit, second = match.groups()
    if damage_type.lower() != effect.get("damage_type"): return effect, residual
    rounds = int(amount) * (600 if unit.lower().startswith("hour") else 10)
    effect.update(zero_hp_stable=True, zero_hp_condition_ids=[first.lower(), second.lower()], zero_hp_duration_rounds=rounds)
    cleaned = (residual[:match.start()] + " " + residual[match.end():]).strip(" .,;")
    return effect, cleaned


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
    timed = _TIMED_REPEAT_CONDITION.search(remainder)
    if timed:
        dc, ability, condition = timed.groups()
        effect = {"save_ability": ability.lower(), "dc": int(dc), "condition_id": condition.lower(), "duration_rounds": 10, "repeat_save_timing": "target_turn_end"}
        residual = (remainder[:timed.start()] + " " + remainder[timed.end():]).strip(" .,;")
        return effect, residual
    disease = _DISEASE_POISON.search(remainder)
    if disease:
        effect = {"save_ability": "constitution", "dc": int(disease.group(1)), "condition_id": "poisoned"}
        residual = (remainder[:disease.start()] + " " + remainder[disease.end():]).strip(" .,;")
        return effect, residual
    for pattern, success in ((_SAVE_DAMAGE_HALF, "half"), (_SAVE_DAMAGE_NONE, "none")):
        match = pattern.search(remainder)
        if match:
            effect = _save_damage_effect(match, success)
            if effect is not None:
                residual = (remainder[:match.start()] + " " + remainder[match.end():]).strip(" .,;")
                return _zero_hp_rider(effect, residual)
    match = _PRONE_SAVE.search(remainder)
    if not match: return None, remainder
    max_size, dc, ability = match.groups()
    effect = {"save_ability": ability.lower(), "dc": int(dc), "condition_id": "prone", "max_target_size": max_size.lower() if max_size else None}
    residual = (remainder[:match.start()] + " " + remainder[match.end():]).strip(" .,;")
    return effect, residual


def parse_on_hit_control(remainder: str) -> tuple[dict | None, bool, str]:
    match = _GRAPPLE.search(remainder)
    if not match: return None, False, remainder
    max_size, dc = match.groups(); before = remainder[:match.start()]; after = remainder[match.end():]
    restrains = bool(_RESTRAINED.search(after)); after = _RESTRAINED.sub(" ", after, count=1)
    forbid = bool(_NO_REPEAT_TARGET.search(after) or _OWN_ATTACK_TARGET.search(after) or _PER_LIMB_GRAPPLE.search(after) or _ALREADY_CONTROLLING.search(after))
    after = _NO_REPEAT_TARGET.sub(" ", after, count=1); after = _OWN_ATTACK_TARGET.sub(" ", after, count=1); after = _PER_LIMB_GRAPPLE.sub(" ", after, count=1); after = _ALREADY_CONTROLLING.sub(" ", after, count=1)
    control = {"grapple_escape_dc": int(dc), "restrains_while_grappled": restrains}
    if max_size: control["max_target_size"] = max_size.lower()
    residual = re.sub(r"^[\s,;]*(?:and\s+)?|[\s,;]+$", "", f"{before} {after}", flags=re.I).strip(" .")
    return control, forbid, residual
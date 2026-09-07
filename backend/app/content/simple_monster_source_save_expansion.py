from __future__ import annotations

import re

_ABILITY = r"Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"
_DAMAGE = r"Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder"
_CONDITION = r"Blinded|Charmed|Deafened|Exhaustion|Frightened|Incapacitated|Paralyzed|Petrified|Poisoned|Prone|Restrained|Stunned|Unconscious"
_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"
_DICE = rf"\d+ \((?P<count>\d+)d(?P<size>\d+)(?P<bonus>\s*[+-]\s*\d+)?\) (?P<type>{_DAMAGE}) damage"
_SINGLE_TIMED = re.compile(
    rf"^(?P<name>.+?)\.(?: [^.]+\.)* (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), one creature .*?within (?P<range>\d+) feet\. "
    rf"Failure: {_DICE}, and the target has the (?P<condition>{_CONDITION}) condition until the (?P<edge>start|end) of (?P<owner>.+?) next turn(?:,[^.]+)?\."
    r"(?: If the target is (?:a )?Large or smaller,[^.]+\.)? Success: (?P<success>Half damage only|Half damage|[^.]+)\.$", re.I,
)
_SIZE_PRONE = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), one creature .*?within (?P<range>\d+) feet\. Failure: {_DICE}\. "
    rf"If the target is a (?P<max_size>{_SIZE}) or smaller creature, it has the (?P<condition>Prone) condition\.$", re.I,
)
_SPACE_DAMAGE_PRONE = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), one (?P<max_size>{_SIZE}) or smaller creature in .+? space\. "
    rf"Failure: {_DICE}, and the target is pushed up to \d+ feet .+? and has the (?P<condition>Prone) condition\. Success: Half damage only\.$", re.I,
)
_CONE_PRONE = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), each creature in a (?P<length>\d+)-foot Cone\. "
    r"Failure: The target is pushed up to \d+ feet .+? and has the (?P<condition>Prone) condition\.$", re.I,
)
_CONE_TIMED = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), each creature in a (?P<length>\d+)-foot Cone\. "
    rf"Failure: The target has the (?P<condition>{_CONDITION}) condition until the (?P<edge>start|end) of (?P<owner>.+?) next turn\.$", re.I,
)
_POINT_TIMED = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), each creature in a (?P<radius>\d+)-foot-radius Sphere centered on a point .*?within (?P<range>\d+) feet\. "
    rf"Failure: {_DICE}, and the target has the (?P<condition>{_CONDITION}) condition until the (?P<edge>start|end) of (?P<owner>.+?) next turn\.$", re.I,
)
_CONE_DAMAGE_SCOPED = re.compile(
    rf"^(?P<name>.+?)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), each creature in a (?P<length>\d+)-foot Cone\. Failure: {_DICE}(?:, and the target’s Speed decreases by \d+ feet until [^.]+)?\. Success: Half damage only\."
    r"(?: Failure or Success: Being underwater doesn’t grant Resistance to this Fire damage\.)?$", re.I,
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _timing(row: dict[str, object], edge: str, owner: str) -> str:
    normalized = owner.lower().replace("’", "'").strip()
    if normalized == "its" or "target" in normalized:
        return f"target_turn_{edge.lower()}"
    if str(row["name"]).lower().replace("’", "'") in normalized:
        return f"source_turn_{edge.lower()}"
    raise ValueError(f"Cannot prove save-condition owner for {row['name']!r}: {owner!r}")


def _base(row: dict[str, object], heading: str, match: re.Match[str], range_ft: int) -> dict[str, object]:
    return {
        "id": f"srd-{_slug(str(row['name']))}-{_slug(heading)}", "name": heading,
        "save_ability": match.group("ability").lower(), "dc": int(match.group("dc")),
        "range_ft": range_ft, "animation": "save-effect",
    }


def _damage(match: re.Match[str]) -> dict[str, object]:
    bonus = int((match.group("bonus") or "0").replace(" ", ""))
    return {
        "damage": {"count": int(match.group("count")), "size": int(match.group("size")), "bonus": bonus},
        "damage_type": match.group("type").lower(),
    }


def _condition(match: re.Match[str], *, timing: str | None = None, max_size: str | None = None) -> dict[str, object]:
    result: dict[str, object] = {"kind": "condition", "condition": match.group("condition").lower()}
    if timing is not None: result["expiry_timing"] = timing
    if max_size is not None: result["max_target_size"] = max_size.lower()
    return result


def parse_expanded_save(row: dict[str, object], heading: str, block: str) -> dict[str, object] | None:
    match = _SINGLE_TIMED.fullmatch(block)
    if match:
        result = _base(row, heading, match, int(match.group("range"))); result.update(_damage(match))
        result["success_damage"] = "half" if match.group("success").lower().startswith("half damage") else "none"
        result["failure_conditions"] = [_condition(match, timing=_timing(row, match.group("edge"), match.group("owner")))]
        return result
    match = _SIZE_PRONE.fullmatch(block)
    if match:
        result = _base(row, heading, match, int(match.group("range"))); result.update(_damage(match))
        result["failure_conditions"] = [_condition(match, max_size=match.group("max_size"))]; return result
    match = _SPACE_DAMAGE_PRONE.fullmatch(block)
    if match:
        result = _base(row, heading, match, 0); result.update(_damage(match)); result["target_max_size"] = match.group("max_size").lower()
        result["success_damage"] = "half"; result["failure_conditions"] = [_condition(match, max_size=match.group("max_size"))]; return result
    match = _CONE_PRONE.fullmatch(block)
    if match:
        result = _base(row, heading, match, int(match.group("length"))); result["area"] = {"shape": "cone", "size_ft": int(match.group("length"))}
        result["failure_conditions"] = [_condition(match)]; return result
    match = _CONE_TIMED.fullmatch(block)
    if match:
        result = _base(row, heading, match, int(match.group("length"))); result["area"] = {"shape": "cone", "size_ft": int(match.group("length"))}
        result["failure_conditions"] = [_condition(match, timing=_timing(row, match.group("edge"), match.group("owner")))]; return result
    match = _POINT_TIMED.fullmatch(block)
    if match:
        result = _base(row, heading, match, int(match.group("range"))); result.update(_damage(match)); result["area"] = {"shape": "radius", "size_ft": int(match.group("radius"))}
        result["failure_conditions"] = [_condition(match, timing=_timing(row, match.group("edge"), match.group("owner")))]; return result
    match = _CONE_DAMAGE_SCOPED.fullmatch(block)
    if match:
        result = _base(row, heading, match, int(match.group("length"))); result.update(_damage(match)); result["area"] = {"shape": "cone", "size_ft": int(match.group("length"))}; result["success_damage"] = "half"; return result
    return None

from __future__ import annotations

import re

from app.content.monster_limited_use_source_audit import parse_action_recharges
from app.content.monster_save_targeting import parse_save_targeting
from app.domain.actions import HitControlEffect, SavingThrowAction
from app.domain.size import CreatureSize

_DAMAGE_TYPES = r"Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder"
_ABILITY = r"Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"
_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"
_SAVE_HEAD = (
    rf"(?P<name>[A-Z][A-Za-z0-9 ’'()/-]+)\.\s+"
    rf"(?P<ability>{_ABILITY})\s+Saving Throw:\s*DC\s*(?P<dc>\d+),\s*(?P<target>[^.]+)\.\s+"
    rf"Failure:\s*\d+\s*\(\s*(?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\s*\)\s+"
    rf"(?P<type>{_DAMAGE_TYPES})\s+damage"
)
_SAVE_DAMAGE = re.compile(_SAVE_HEAD + r"\.\s*(?P<success>Success:\s*Half damage\.)?", re.I)
_SAVE_DAMAGE_GRAPPLE = re.compile(
    _SAVE_HEAD
    + r",\s+and\s+the target has the Grappled condition \(escape DC (?P<escape>\d+)\)\."
    + r"(?P<restrained>\s*While Grappled, the target has the Restrained condition\.)?"
    + r"\s*(?P<success>Success:\s*Half damage\.)?",
    re.I,
)
_SAVE_DAMAGE_PRONE = re.compile(
    _SAVE_HEAD
    + rf"\.\s+If the target is a (?P<condition_size>{_SIZE}) or smaller creature, "
    + r"(?:it|the target) has the Prone condition\."
    + r"\s*(?P<success>Success:\s*Half damage\.)?",
    re.I,
)
_RECHARGE_SUFFIX = re.compile(r"\s*\(\s*Recharge\s+\d(?:\s*[-–]\s*\d)?\s*\)\s*$", re.I)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _action(match: re.Match[str], monster_slug: str, recharges: dict[str, int]) -> SavingThrowAction:
    printed = match.group("name").strip(); name = _RECHARGE_SUFFIX.sub("", printed).strip()
    range_ft, area, target_size = parse_save_targeting(match.group("target"))
    bonus = int(match.group("bonus") or 0) * (-1 if match.group("sign") == "-" else 1)
    resource_id = f"srd-{monster_slug}-{_slug(name)}-recharge" if name in recharges else None
    failure_control = None; escape_dc = None; restrains = False
    if "escape" in match.re.groupindex:
        escape = match.group("escape")
        if escape:
            escape_dc = int(escape); restrains = bool(match.group("restrained"))
            failure_control = HitControlEffect(
                max_target_size=target_size,
                grapple_escape_dc=escape_dc,
                restrains_while_grappled=restrains,
            )
    if "condition_size" in match.re.groupindex and match.group("condition_size"):
        failure_control = HitControlEffect(
            max_target_size=CreatureSize(match.group("condition_size").lower()),
            condition_id="prone",
        )
    return SavingThrowAction(
        id=f"srd-{monster_slug}-{_slug(name)}", name=name,
        save_ability=match.group("ability").lower(), dc=int(match.group("dc")),
        range_ft=range_ft, area=area, target_max_size=target_size,
        damage_dice_count=int(match.group("count")), damage_dice_size=int(match.group("size")),
        damage_bonus=bonus, damage_type=match.group("type").lower(),
        success_damage="half" if match.group("success") else "none", failure_control=failure_control,
        grapple_escape_dc=escape_dc, restrains_while_grappled=restrains,
        resource_id=resource_id, animation="save-effect",
    )


def _save_matches(actions: str) -> list[re.Match[str]]:
    matches = [*_SAVE_DAMAGE_GRAPPLE.finditer(actions), *_SAVE_DAMAGE_PRONE.finditer(actions)]
    occupied = [(match.start(), match.end()) for match in matches]
    matches.extend(
        match for match in _SAVE_DAMAGE.finditer(actions)
        if not any(start <= match.start() < end for start, end in occupied)
    )
    return sorted(matches, key=lambda item: item.start())


def parse_simple_save_actions(row: dict[str, object]) -> list[SavingThrowAction]:
    try:
        actions = str(row.get("actions", "")); recharges = parse_action_recharges(row); monster_slug = _slug(str(row["name"]))
        return [_action(match, monster_slug, recharges) for match in _save_matches(actions)]
    except (TypeError, ValueError, KeyError) as exc:
        raise ValueError(f"simple save parsing failed for {row.get('name', '<unknown>')}") from exc


def strip_simple_save_actions(actions: str) -> str:
    """Remove only clauses that fully match audited simple save/damage/control grammar."""
    clean = actions
    for match in reversed(_save_matches(actions)):
        try:
            parse_save_targeting(match.group("target"))
        except ValueError:
            continue
        clean = clean[:match.start()] + " " + clean[match.end():]
    return clean

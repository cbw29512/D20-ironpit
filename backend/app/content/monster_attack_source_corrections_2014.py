from __future__ import annotations

import html
import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014

logger = logging.getLogger(__name__)

_SCOUT_LONGBOW_SIGNATURE = (
    "Longbow", "ranged", 4,
    6, 1, 8, 2, "piercing",
)
_SCOUT_LONGBOW_RANGE = (150, 600)


# A ranged spell attack has one maximum range, unlike a normal/long weapon band.
# This exact-source matcher repairs missing parser bands without inventing
# long-range disadvantage or hardcoding any monster/ability as engine behavior.
_SINGLE_RANGE_SPELL_ATTACK = re.compile(
    r"(?P<name>[A-Za-z][A-Za-z '\\-]+)\\.\\s*Ranged Spell Attack:\\s*"
    r"\\+(?P<bonus>\\d+) to hit,\\s*range (?P<range>\\d+) ft\\.,\\s*"
    r"one target\\.\\s*Hit:\\s*(?P<average>\\d+) "
    r"\\((?P<count>\\d+)d(?P<size>\\d+)\\) "
    r"(?P<damage_type>[a-z]+) damage",
    re.IGNORECASE,
)


def _printed_single_spell_range_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> int | None:
    """Require source attack name, bonus, dice and damage to agree before binding."""
    try:
        if attack.kind != "ranged" or attack.damage.bonus != 0:
            return None
        printed = " ".join(
            html.unescape(re.sub(r"<[^>]*>", " ", monster.source_actions or "")).split()
        )
        for match in _SINGLE_RANGE_SPELL_ATTACK.finditer(printed):
            parts = match.groupdict()
            if parts["name"].strip().casefold() != attack.name.strip().casefold():
                continue
            signature = (
                int(parts["bonus"]), int(parts["average"]),
                int(parts["count"]), int(parts["size"]), parts["damage_type"].lower(),
            )
            expected = (
                attack.attack_bonus, attack.damage.average, attack.damage.dice_count,
                attack.damage.dice_size, str(attack.damage.type).lower(),
            )
            if signature != expected:
                raise ValueError(
                    f"2014 ranged-spell source differs from parsed attack {monster.id}/{attack.id}: "
                    f"{signature!r} != {expected!r}"
                )
            return int(parts["range"])
        return None
    except Exception:
        logger.exception("2014 source ranged-spell range parsing failed for %s/%s.", monster.id, attack.id)
        raise


def corrected_attack_range_2014(
    monster: SourceMonster2014,
    attack: SourceAttack2014,
) -> tuple[int | None, int | None]:
    """Apply reviewed 2014 parser range corrections without mutating source data."""
    try:
        current = (attack.normal_range_ft, attack.long_range_ft)
        if (monster.id, attack.id) != ("scout", "longbow"):
            # Reuse the source-verified, single-range spell-attack primitive.
            # This is immutable source binding; the browser/Python attack range
            # resolvers continue to use the same existing range-band mechanic.
            if current[0] is not None and current[1] is not None:
                return current
            printed_range = _printed_single_spell_range_2014(monster, attack)
            if printed_range is None:
                return current
            if any(v is not None and v != printed_range for v in current):
                raise ValueError(
                    f"2014 single-range spell contradicts parsed attack "
                    f"{monster.id}/{attack.id}: {current!r} != {printed_range!r}"
                )
            return (printed_range, printed_range)

        signature = (
            attack.name, attack.kind, attack.attack_bonus,
            attack.damage.average, attack.damage.dice_count,
            attack.damage.dice_size, attack.damage.bonus, attack.damage.type,
        )
        if signature != _SCOUT_LONGBOW_SIGNATURE:
            raise RuntimeError(
                f"2014 Scout Longbow source drift: {signature!r} != "
                f"{_SCOUT_LONGBOW_SIGNATURE!r}"
            )
        if current == _SCOUT_LONGBOW_RANGE:
            return current
        if current[0] not in (None, _SCOUT_LONGBOW_RANGE[0]) or current[1] not in (
            None, _SCOUT_LONGBOW_RANGE[1]
        ):
            raise RuntimeError(
                f"2014 Scout Longbow range drift: {current!r} is not a partial "
                f"{_SCOUT_LONGBOW_RANGE!r} parse."
            )
        return _SCOUT_LONGBOW_RANGE
    except Exception:
        logger.exception(
            "Failed to apply 2014 attack-range source correction for %s/%s.",
            monster.id,
            attack.id,
        )
        raise

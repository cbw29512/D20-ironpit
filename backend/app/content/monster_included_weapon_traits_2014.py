"""Validate traits whose damage is already included in pinned weapon attacks."""
from __future__ import annotations

from html import unescape
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.weapons import DamageSourceQualifier

logger = logging.getLogger(__name__)
_TRAITS = {
    "Brute": re.compile(
        r"A melee weapon deals one extra die of its damage when .+? hits with it "
        r"\(included in the attack\)\.", re.I,
    ),
    "Heated Weapons": re.compile(
        r"(?:When .+? hits with a metal melee weapon, it deals an extra "
        r"|Any metal melee weapon .+? wields deals an extra )"
        r"\d+ \((\d+)d(\d+)\) fire damage(?: on a hit)? \(included in the attack\)\.", re.I,
    ),
    "Angelic Weapons": re.compile(
        r".+? weapon attacks are magical\. When .+? hits with any weapon, "
        r"the weapon deals an extra (\d+)d(\d+) radiant damage "
        r"\(included in the attack\)\.", re.I,
    ),
}
_DAMAGE = re.compile(r"\((\d+)d(\d+)(?:\s*\+\s*(\d+))?\)\s+(\w+) damage", re.I)


def _sections(source: str | None) -> dict[str, str]:
    try:
        sections = {}
        for paragraph in re.findall(r"<p>(.*?)</p>", source or "", re.S):
            heading = re.search(r"<strong>(.*?)</strong>", paragraph, re.S)
            if heading:
                name = unescape(re.sub(r"<[^>]*>", "", heading[1])).rstrip(".")
                body = re.sub(r"<[^>]*>", "", paragraph[heading.end():])
                sections[name] = " ".join(unescape(body).split())
        return sections
    except Exception:
        logger.exception("Failed to read included weapon source sections.")
        raise


def _validated_trait(monster: SourceMonster2014, name: str, text: str) -> bool:
    try:
        match = _TRAITS[name].fullmatch(text)
        if match is None or not monster.attacks:
            return False
        rider = None if name == "Brute" else (
            int(match[1]), int(match[2]), 0,
            "fire" if name == "Heated Weapons" else "radiant",
        )
        actions = _sections(monster.source_actions)
        included = 0
        for attack in monster.attacks:
            action = actions.get(attack.name, "")
            if "Weapon Attack:" not in action:
                return False
            printed = {(int(n), int(d), int(b or 0), t.lower())
                       for n, d, b, t in _DAMAGE.findall(action)}
            base = attack.damage
            base_tuple = (base.dice_count, base.dice_size, base.bonus, base.type)
            if base_tuple not in printed:
                return False
            rows = attack.on_hit_damage
            if not all(isinstance(row, dict) for row in rows):
                return False
            payloads = [(row.get("dice_count"), row.get("dice_size"),
                         row.get("bonus", 0), row.get("type")) for row in rows]
            if len(set(payloads)) != len(payloads) or any(
                payload not in printed - {base_tuple} for payload in payloads
            ):
                return False
            if rider is None:
                if attack.kind == "melee" and base.dice_count < 2:
                    return False
                included += attack.kind == "melee"
            elif rider in printed:
                if payloads.count(rider) != 1:
                    return False
                included += 1
            elif name == "Angelic Weapons":
                return False
        return included > 0
    except Exception:
        logger.exception("Failed to validate included weapon trait %s for %s.", name, monster.id)
        raise


def included_weapon_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    try:
        requested = set(monster.trait_names) & _TRAITS.keys()
        if not requested:
            return frozenset()
        traits = _sections(monster.source_traits)
        bound = {name for name in requested if _validated_trait(monster, name, traits.get(name, ""))}
        for name in requested - bound:
            logger.warning("Unbound included weapon trait %s for %s: source/payload mismatch.", name, monster.id)
        return frozenset(bound)
    except Exception:
        logger.exception("Failed to bind included weapon traits for %s.", monster.id)
        raise


def weapon_damage_source_qualifiers_2014(monster: SourceMonster2014) -> list[DamageSourceQualifier]:
    try:
        magical = "Magic Weapons" in monster.trait_names or (
            "Angelic Weapons" in included_weapon_trait_names_2014(monster)
        )
        return [DamageSourceQualifier.MAGICAL] if magical else []
    except Exception:
        logger.exception("Failed to bind weapon damage source qualifiers for %s.", monster.id)
        raise

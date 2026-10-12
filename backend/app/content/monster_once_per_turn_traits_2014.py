from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider

logger = logging.getLogger(__name__)
_MARTIAL_ADVANTAGE = "Martial Advantage"
_MARTIAL_BODY = re.compile(
    r"Martial Advantage\.</strong></em>\s*(.*?)</p>",
    re.IGNORECASE | re.DOTALL,
)
_ONCE_PER_TURN = re.compile(r"\bonce\s+per\s+turn\b", re.IGNORECASE)
_WEAPON_HIT = re.compile(r"hits?\s+with\s+a\s+weapon\s+attack\b", re.IGNORECASE)
_DAMAGE_DICE = re.compile(
    r"extra\s+\d+\s+\((\d+)d(\d+)\)\s+damage",
    re.IGNORECASE | re.DOTALL,
)
_ADJACENCY = re.compile(
    r"within\s+5\s+feet\s+of\s+an\s+ally.*?isn['’]t\s+incapacitated",
    re.IGNORECASE | re.DOTALL,
)


def martial_advantage_rider_2014(
    monster: SourceMonster2014,
) -> OncePerTurnWeaponHitDamageRider | None:
    """Compile printed Martial Advantage into a shared adjacent-ally hit rider."""
    try:
        if _MARTIAL_ADVANTAGE not in monster.trait_names:
            return None
        source = monster.source_traits or ""
        body_match = _MARTIAL_BODY.search(source)
        if body_match is None:
            raise ValueError(f"{monster.name} has no isolated Martial Advantage source body.")
        body = body_match.group(1)
        damage = _DAMAGE_DICE.search(body)
        if (
            _ONCE_PER_TURN.search(body) is None
            or _WEAPON_HIT.search(body) is None
            or damage is None
            or _ADJACENCY.search(body) is None
        ):
            raise ValueError(f"{monster.name} has unsupported Martial Advantage wording.")
        count, size = int(damage.group(1)), int(damage.group(2))
        return OncePerTurnWeaponHitDamageRider(
            source_id="martial-advantage",
            source_name=_MARTIAL_ADVANTAGE,
            dice_count=count,
            dice_size=size,
            requires_active_ally_adjacent_to_target=True,
        )
    except Exception:
        logger.exception("Failed to bind 2014 Martial Advantage for %s.", monster.name)
        raise


def surprise_attack_rider_2014(
    monster: SourceMonster2014,
) -> OncePerTurnWeaponHitDamageRider | None:
    """Bind the Bugbear's printed dice to the locked first-initiative Pit policy.

    This is content-source selection, never monster-ID combat dispatch.
    Doppelganger and 2024 source behavior remain independently unbound.
    """
    try:
        if monster.id != "bugbear" or "Surprise Attack" not in monster.trait_names:
            return None
        # Strip presentation markup so exact printed parameters can be verified.
        import html
        source = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", monster.source_traits or "")).split())
        lowered = source.casefold()
        if not all(phrase in lowered for phrase in (
            "surprise attack.", "surprises a creature",
            "hits it with an attack during the first round of combat",
        )):
            raise ValueError("Bugbear Surprise Attack source trigger is incomplete.")
        match = re.search(r"extra\s+7\s+\((\d+)d(\d+)\)\s+damage", source, re.IGNORECASE)
        if match is None:
            raise ValueError("Bugbear Surprise Attack source damage is incomplete.")
        return OncePerTurnWeaponHitDamageRider(
            source_id="surprise-attack",
            source_name="Surprise Attack",
            dice_count=int(match.group(1)),
            dice_size=int(match.group(2)),
            requires_first_attack_of_fight=True,
            requires_attacker_first_turn=True,
            requires_target_unacted=True,
        )
    except Exception:
        logger.exception("Failed to bind 2014 Surprise Attack for %s.", monster.name)
        raise

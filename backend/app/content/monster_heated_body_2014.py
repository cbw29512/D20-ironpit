from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_fire_form_entry_2014 import fire_form_space_entry_2014
from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

# A complete source clause is required. A trait label by itself cannot
# certify a retaliation. Stop at the next printed trait boundary.
_CONTACT = re.compile(
    r"A creature that touches the .+? or hits it with a melee attack "
    r"while within (?P<reach>\d+) feet of it takes "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+)\) (?P<type>fire|acid) damage\b",
    re.IGNORECASE | re.DOTALL,
)


def _source_retaliation_2014(
    monster: SourceMonster2014, label: str, damage_type: DamageType,
) -> list[TimedSelfBuffAction]:
    if label not in monster.trait_names:
        return []
    source = monster.source_traits or ""
    heading = re.compile(
        rf"<strong>{re.escape(label)}\.</strong>(?P<body>.*?)(?=<strong>|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    section = heading.search(source)
    if section is None:
        return []
    match = _CONTACT.search(section.group("body"))
    if match is None or match.group("type").lower() != damage_type.value:
        return []
    if int(match.group("average")) != (int(match.group("count")) * (int(match.group("size")) + 1)) // 2:
        return []
    return [TimedSelfBuffAction(
        id=label.lower().replace(" ", "-"), name=label, activation_timing="passive",
        melee_hit_retaliation=MeleeHitRetaliation(
            range_ft=int(match.group("reach")),
            dice_count=int(match.group("count")),
            dice_size=int(match.group("size")),
            damage_type=damage_type,
            on_contact=True,
        ),
    )]


def heated_body_retaliation_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Preserve 2014 fire parameters with a generic passive retaliation rule."""
    try:
        return _source_retaliation_2014(monster, "Heated Body", DamageType.FIRE)
    except Exception:
        logger.exception("Failed 2014 Heated Body binding for %s.", monster.name)
        raise


def corrosive_form_retaliation_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Bind the printed Acid hit/contact clause; equipment damage is Pit-neutral."""
    try:
        return _source_retaliation_2014(monster, "Corrosive Form", DamageType.ACID)
    except Exception:
        logger.exception("Failed 2014 Corrosive Form binding for %s.", monster.name)
        raise



def fire_form_contact_retaliation_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Reuse the same contact/melee retaliation for a compound Fire Form trait.

    This binds ONLY the printed contact clause. Space-entry ignition and water
    interactions are separate obligations and keep the monster blocked.
    """
    try:
        from app.content.monster_source_sections_2014 import source_sections_2014

        body = source_sections_2014(monster.source_traits, include_continuations=True).get("Fire Form")
        if body is None:
            return []
        # Fail closed when the other independent clauses are altered: this is
        # a partial binding, not certification of the entire compound trait.
        required = (
            "can move through a space as narrow as 1 inch wide without squeezing",
            "can enter a hostile creature's space and stop there",
            "first time it enters a creature's space on a turn",
            "catches fire",
            "at the start of each of its turns",
        )
        if not all(text in body for text in required):
            return []
        actions = _source_retaliation_2014(monster, "Fire Form", DamageType.FIRE)
        entry = fire_form_space_entry_2014(monster)
        return [action.model_copy(update={"hostile_space_entry_damage": entry}) for action in actions]
    except Exception:
        logger.exception("Failed generic 2014 Fire Form contact-damage binding.")
        raise

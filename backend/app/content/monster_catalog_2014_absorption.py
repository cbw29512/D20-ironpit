from __future__ import annotations

import re

from app.domain.damage_defense_rules import DamageAbsorption

_ABSORPTION = re.compile(
    r"(?P<name>[A-Za-z ]+ Absorption)\.\s*Whenever the [^.]+ is subjected to (?P<dtype>\w+) damage, "
    r"it takes no damage and instead regains a number of hit points equal to the (?P=dtype) damage dealt\.",
    re.I,
)


def damage_absorptions_2014(source_traits: str | None) -> list[DamageAbsorption]:
    if not source_traits or "Absorption." not in source_traits:
        return []
    text = re.sub(r"<[^>]+>", "", source_traits)
    return [DamageAbsorption(damage_type=match.group("dtype").lower()) for match in _ABSORPTION.finditer(text)]

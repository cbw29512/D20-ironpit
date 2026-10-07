from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.damage_triggered_d20 import DamageTriggeredD20Debuff
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_SUPPORTED_NAMES = frozenset({"Fear of Fire", "Aversion of Fire"})
_TAGS = re.compile(r"<[^>]+>")
_SEMANTIC = re.compile(
    r"^If\s+the\s+.+?\s+takes\s+([a-z]+)\s+damage,\s+"
    r"it\s+has\s+disadvantage\s+on\s+attack\s+rolls\s+and\s+ability\s+checks\s+"
    r"until\s+the\s+end\s+of\s+its\s+next\s+turn\.$",
    re.IGNORECASE,
)


def _trait_body(source: str, name: str) -> str | None:
    pattern = re.compile(
        rf"<em><strong>{re.escape(name)}\.</strong></em>\s*(.*?)</p>",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(source)
    if match is None:
        return None
    return " ".join(_TAGS.sub("", match.group(1)).split())


def damage_triggered_d20_debuffs_2014(
    monster: SourceMonster2014,
) -> list[DamageTriggeredD20Debuff]:
    """Compile printed typed-damage self-debuffs into one universal trigger."""
    try:
        rules: list[DamageTriggeredD20Debuff] = []
        source = monster.source_traits or ""
        for source_name in _SUPPORTED_NAMES.intersection(monster.trait_names):
            body = _trait_body(source, source_name)
            if body is None:
                raise ValueError(f"{monster.name} has no isolated {source_name} source body.")
            match = _SEMANTIC.fullmatch(body)
            if match is None:
                raise ValueError(f"{monster.name} has unsupported {source_name} wording.")
            rules.append(DamageTriggeredD20Debuff(
                source_id=source_name.casefold().replace(" ", "-"),
                source_name=source_name,
                trigger_damage_type=DamageType(match.group(1).casefold()),
                trigger_damage_minimum=1,
                attack_roll_disadvantage=True,
                ability_check_disadvantage=True,
                duration_target_turns=1,
            ))
        return sorted(rules, key=lambda item: item.source_id)
    except (TypeError, ValueError):
        logger.exception("Failed to bind damage-triggered D20 debuffs for %s.", monster.name)
        raise
    except Exception as exc:
        logger.exception("Unexpected damage-triggered D20 binding failure for %s.", monster.name)
        raise RuntimeError("Damage-triggered D20 debuffs could not be bound.") from exc

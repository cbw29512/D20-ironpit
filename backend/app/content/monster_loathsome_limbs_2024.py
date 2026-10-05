from __future__ import annotations

import logging
import re

from app.content.monster_catalog import load_monster_rows
from app.domain.triggered_extra_attacks import TriggeredExtraAttackStack
from app.domain.weapons import DamageType, Weapon, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)

_TRIGGER = re.compile(
    r"Loathsome Limbs \((\d+)/Day\)\. If the \w+ ends any turn Bloodied and took "
    r"(\d+)\+ ([A-Za-z]+) damage during that turn, .* becomes a ([A-Za-z ]+)\. "
    r"The limb acts immediately after the \w+[’']s turn\. "
    r"The \w+ has (\d+) Exhaustion level for each missing limb, and it grows replacement limbs "
    r"the next time it regains Hit Points\.",
    re.I,
)
_ATTACK = re.compile(
    r"([A-Za-z ]+)\. Melee Attack Roll: \+(\d+), reach (\d+) ft\. "
    r"Hit: \d+ \((\d+)d(\d+) \+ (\d+)\) ([A-Za-z]+) damage\.",
    re.I,
)


def _row(name: str) -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == name]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD 5.2.1 row for {name!r}; found {len(rows)}.")
    return rows[0]


def loathsome_limbs_stack_2024(source_traits: object) -> TriggeredExtraAttackStack | None:
    """Compile the printed limb-spawn rule into the approved Iron Pit attached-attack abstraction."""
    try:
        text = str(source_traits or "")
        if "Loathsome Limbs" not in text:
            return None
        match = _TRIGGER.search(text)
        if match is None:
            raise ValueError("Loathsome Limbs source wording is unsupported.")
        uses = int(match.group(1))
        threshold = int(match.group(2))
        damage_type = DamageType(match.group(3).lower())
        spawned_name = match.group(4).strip()
        exhaustion = int(match.group(5))

        spawned = _row(spawned_name)
        attack_match = _ATTACK.search(str(spawned.get("actions", "")))
        if attack_match is None:
            raise ValueError(f"{spawned_name} attack source wording is unsupported.")
        attack_name = attack_match.group(1).strip()
        attack_bonus = int(attack_match.group(2))
        reach = int(attack_match.group(3))
        dice_count = int(attack_match.group(4))
        dice_size = int(attack_match.group(5))
        damage_bonus = int(attack_match.group(6))
        attack_damage_type = DamageType(attack_match.group(7).lower())
        attack_id = "iron-pit-attached-" + re.sub(r"[^a-z0-9]+", "-", spawned_name.lower()).strip("-") + "-rend"
        attack = WeaponAttack(
            id=attack_id,
            weapon=Weapon(
                id=f"{attack_id}-weapon",
                name=attack_name,
                attack_kind=WeaponAttackKind.MELEE,
                dice_count=dice_count,
                dice_size=dice_size,
                damage_type=attack_damage_type,
                animation="strike",
                reach_ft=reach,
            ),
            attack_bonus=attack_bonus,
            damage_bonus=damage_bonus,
        )
        return TriggeredExtraAttackStack(
            source_id="loathsome-limbs",
            source_name="Loathsome Limbs",
            trigger_damage_type=damage_type,
            trigger_damage_minimum=threshold,
            requires_bloodied=True,
            max_stacks=uses,
            max_uses=uses,
            exhaustion_per_stack=exhaustion,
            attack=attack,
            clears_on_regeneration_heal=True,
        )
    except Exception:
        logger.exception("Failed to compile 2024 Loathsome Limbs source.")
        raise

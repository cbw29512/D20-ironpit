from __future__ import annotations

import re

from app.domain.models import WeaponAttack


def ability_reduction_issues(attack: WeaponAttack, actions: str) -> list[str]:
    rider = attack.ability_score_reduction_on_hit
    if rider is None:
        return []
    ability = re.escape(rider.ability.title())
    dice = rf"{rider.dice_count}\s*d\s*{rider.dice_size}"
    decrease = re.compile(
        rf"target[’']s\s+{ability}\s+score\s+decreases\s+by\s+{dice}",
        re.IGNORECASE,
    )
    issues: list[str] = []
    if not decrease.search(actions):
        issues.append(f"ability-score-reduction-mismatch:{attack.id}:{rider.ability}")
    if rider.dies_at_minimum:
        death = re.compile(
            rf"target\s+dies\s+if\s+this\s+reduces\s+that\s+score\s+to\s+{rider.minimum_score}\b",
            re.IGNORECASE,
        )
        if not death.search(actions):
            issues.append(f"ability-score-reduction-death-mismatch:{attack.id}:{rider.ability}")
    return issues

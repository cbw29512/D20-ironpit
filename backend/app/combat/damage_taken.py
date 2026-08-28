from __future__ import annotations

import logging
from collections import defaultdict

from app.domain.models import CombatantState, DamageRollComponent, DamageType

logger = logging.getLogger(__name__)


def resolve_damage_taken(
    defender: CombatantState,
    components: list[DamageRollComponent],
) -> tuple[int, set[DamageType], set[DamageType], set[DamageType]]:
    """Apply immunity/resistance/vulnerability by damage type for one damage instance."""
    try:
        totals: dict[DamageType, int] = defaultdict(int)
        for component in components:
            totals[component.damage_type] += max(0, component.total)

        resistances = defender.template.damage_resistances | defender.temporary_damage_resistances
        immunities = defender.template.damage_immunities
        vulnerabilities = defender.template.damage_vulnerabilities
        applied = 0
        resisted: set[DamageType] = set()
        immune: set[DamageType] = set()
        vulnerable: set[DamageType] = set()

        for damage_type, raw in totals.items():
            if damage_type in immunities:
                immune.add(damage_type)
                continue
            resistant = damage_type in resistances
            vulnerable_to = damage_type in vulnerabilities
            amount = raw
            if resistant and not vulnerable_to:
                amount //= 2
                resisted.add(damage_type)
            elif vulnerable_to and not resistant:
                amount *= 2
                vulnerable.add(damage_type)
            applied += amount
        return applied, resisted, immune, vulnerable
    except Exception as exc:
        logger.exception("Damage mitigation failed for %s.", defender.template.name)
        raise RuntimeError("Damage mitigation could not be resolved.") from exc

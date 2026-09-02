from __future__ import annotations

from app.domain.models import CombatantState, WeaponAttack

TACTICAL_MASTER_REPLACEMENT = "Sap"


def tactical_master_sap_selected(state: CombatantState, attack: WeaponAttack) -> bool:
    """Return whether this attack explicitly replaces its normal mastery with Sap."""
    return (
        attack.weapon.id in state.template.weapon_masteries
        and attack.weapon.id in state.template.progression_features.tactical_master_sap_weapon_ids
    )

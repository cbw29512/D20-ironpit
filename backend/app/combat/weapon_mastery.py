from __future__ import annotations

from app.combat.tactical_master_policy import tactical_master_sap_selected
from app.domain.models import CombatantState, WeaponAttack


def weapon_is_mastered(state: CombatantState, attack: WeaponAttack) -> bool:
    """Return whether this combatant selected mastery for the attack's weapon."""
    return attack.weapon.id in state.template.weapon_masteries


def weapon_mastery_active(
    state: CombatantState,
    attack: WeaponAttack,
    mastery_property: str,
) -> bool:
    """Return the weapon's normal mastery only when Tactical Master did not replace it."""
    return (
        attack.weapon.mastery_property == mastery_property
        and weapon_is_mastered(state, attack)
        and not tactical_master_sap_selected(state, attack)
    )

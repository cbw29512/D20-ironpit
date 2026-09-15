from __future__ import annotations

from app.combat.tactical_master_policy import tactical_master_sap_selected
from app.domain.models import CombatantState, WeaponAttack


def weapon_is_owned(state: CombatantState, attack: WeaponAttack) -> bool:
    """Return whether the attack's weapon is present on this combatant's template."""
    owned_attacks = (state.template.weapon_attack, *state.template.alternate_weapon_attacks)
    return any(candidate.weapon.id == attack.weapon.id for candidate in owned_attacks)


def weapon_is_mastered(state: CombatantState, attack: WeaponAttack) -> bool:
    """Return whether 2024 mastery is assigned to an owned weapon."""
    return (
        state.template.ruleset == "2024"
        and weapon_is_owned(state, attack)
        and attack.weapon.id in state.template.weapon_masteries
    )


def weapon_mastery_active(
    state: CombatantState,
    attack: WeaponAttack,
    mastery_property: str,
) -> bool:
    """Return the weapon's mastery only when it is authorized and not replaced."""
    return (
        attack.weapon.mastery_property == mastery_property
        and weapon_is_mastered(state, attack)
        and not tactical_master_sap_selected(state, attack)
    )

from __future__ import annotations

from app.domain.models import CombatantState, WeaponAttack


def weapon_is_mastered(state: CombatantState, attack: WeaponAttack) -> bool:
    """Return whether this combatant selected mastery for the attack's weapon."""
    return attack.weapon.id in state.template.weapon_masteries


def weapon_mastery_active(
    state: CombatantState,
    attack: WeaponAttack,
    mastery_property: str,
) -> bool:
    """Universal Weapon Mastery predicate shared by every combatant."""
    return (
        attack.weapon.mastery_property == mastery_property
        and weapon_is_mastered(state, attack)
    )

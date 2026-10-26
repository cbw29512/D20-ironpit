"""Apply source-declared corrosion only after an eligible weapon hit resolves."""
from __future__ import annotations

from app.combat.weapon_corrosion import corrode_weapon_after_hit
from app.domain.models import CombatantState, WeaponAttack


def resolve_weapon_hit_corrosion(
    attacker: CombatantState, defender: CombatantState, attack: WeaponAttack,
) -> int | None:
    """Return stack penalty, or None without complete attacker/target evidence."""
    rule = defender.template.weapon_hit_corrosion
    if rule is None:
        return None
    weapon = attack.weapon
    # Ammunition and ranged-weapon body materials are not interchangeable.
    # Do not corrode a bow when the projectile is the qualifying metal item.
    if weapon.attack_kind.value == "ranged":
        return None
    if weapon.material is None or weapon.is_magical is None:
        return None
    if weapon.material not in rule.qualifying_materials:
        return None
    if rule.requires_nonmagical and weapon.is_magical:
        return None
    return corrode_weapon_after_hit(
        attacker, weapon.id, hit=True, nonmagical_metal=True,
    )

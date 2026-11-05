from __future__ import annotations

"""Foundation for 2014 Gray Ooze Corrode Metal.

Printed 2014 Corrode Metal:
Any nonmagical weapon made of metal that hits the ooze corrodes. After dealing
damage, the weapon takes a permanent and cumulative −1 penalty to damage rolls.
If its penalty drops to −5, the weapon is destroyed. Nonmagical ammunition made
of metal that hits the ooze is destroyed after dealing damage.
The ooze can eat through 2-inch-thick, nonmagical metal in 1 round.

Shared semantic: on hit by nonmagical metal weapon/ammo, apply cumulative
damage-roll penalty (destroy at −5) or destroy ammo. Metal-eating is
arena-context dependent. No name dispatch.
Next wiring: bind to universal on-hit equipment-state primitives with
Python/browser parity. Does not claim admission or clear blockers.
"""


def corrode_metal_notes() -> dict[str, object]:
    return {
        "monster": "Gray Ooze",
        "trait": "Corrode Metal",
        "effect": "cumulative −1 damage penalty on nonmagical metal weapons (destroy at −5); destroy metal ammo; eat nonmagical metal",
        "status": "foundation",
    }

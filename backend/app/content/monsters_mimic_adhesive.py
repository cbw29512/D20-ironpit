from __future__ import annotations

"""Foundation for 2014 Mimic Adhesive.

Printed 2014 Adhesive (Object Form Only):
The mimic adheres to anything that touches it. A Huge or smaller creature
adhered to the mimic is also grappled by it (escape DC 13). Ability checks
made to escape this grapple have disadvantage.

Next wiring: bind the on-touch grapple so it resolves in combat.
Does not claim admission.
"""


def mimic_adhesive_notes() -> dict[str, object]:
    return {
        "monster": "Mimic",
        "trait": "Adhesive",
        "condition": "object form only",
        "effect": "on-touch grapple, escape DC 13 with disadvantage",
    }

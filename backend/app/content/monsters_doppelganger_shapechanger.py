from __future__ import annotations

"""Foundation for 2014 Doppelganger Shapechanger.

Printed 2014 Shapechanger:
The doppelganger can use its action to polymorph into a Small or Medium
humanoid it has seen, or back into its true form. Its statistics, other than
its size, are the same in each form. Any equipment it is wearing or carrying
isn't transformed. It reverts to its true form if it dies.

Next wiring: bind the form change so it resolves in combat. Does not claim
admission.
"""


def doppelganger_shapechanger_notes() -> dict[str, object]:
    return {
        "monster": "Doppelganger",
        "trait": "Shapechanger",
        "cost": "action",
        "effect": "polymorph into a Small or Medium humanoid it has seen, or back to true form",
        "revert": "reverts to true form on death",
    }

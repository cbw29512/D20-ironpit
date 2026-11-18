from __future__ import annotations

"""Foundation for 2014 Chuul Sense Magic.

Printed 2014 Sense Magic:
The chuul senses magic within 120 feet of it at will. This trait otherwise works
like the detect magic spell but isn't itself magical.

Next wiring: bind the passive magic detection so it resolves in combat (vision/
sensory gating). Does not claim admission.
"""


def chuul_sense_magic_notes() -> dict[str, object]:
    return {
        "monster": "Chuul",
        "trait": "Sense Magic",
        "range": "120 feet",
        "effect": "senses magic at will (like detect magic, non-magical)",
    }

from __future__ import annotations

"""Foundation for 2014 Cloaker Light Sensitivity.

Printed 2014 Light Sensitivity:
While in bright light, the cloaker has disadvantage on attack rolls and
Wisdom (Perception) checks that rely on sight.

Next wiring: bind the bright-light disadvantage to the existing vision/
condition primitives so it resolves in combat. Does not claim admission.
"""


def cloaker_light_sensitivity_notes() -> dict[str, object]:
    return {
        "monster": "Cloaker",
        "trait": "Light Sensitivity",
        "effect": "disadvantage on attack rolls and sight-based Perception in bright light",
    }

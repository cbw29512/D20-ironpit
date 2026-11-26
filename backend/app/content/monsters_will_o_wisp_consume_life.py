from __future__ import annotations

"""Foundation for 2014 Will-o'-Wisp Consume Life.

Printed 2014 Consume Life:
As a bonus action, the will-o'-wisp can target one creature it can see within
5 feet of it that has 0 hit points and is still alive. The target must succeed
on a DC 10 Constitution saving throw against this magic or die. If the target
dies, the will-o'-wisp regains 3d6 hit points.

Next wiring: bind the zero-HP death save and healing rider so it resolves in
combat. Does not claim admission.
"""


def will_o_wisp_consume_life_notes() -> dict[str, object]:
    return {
        "monster": "Will-o'-Wisp",
        "ability": "Consume Life",
        "cost": "bonus action",
        "target": "0-HP living creature within 5 ft",
        "save": "DC 10 Con or die",
        "rider": "regain 3d6 HP if target dies",
    }

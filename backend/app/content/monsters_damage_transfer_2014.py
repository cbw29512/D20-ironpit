from __future__ import annotations

"""Foundation for 2014 Damage Transfer semantic family.

Source-verified 2014 printed text:

Cloaker Damage Transfer:
While attached to a creature, the cloaker takes only half the damage dealt to it
(rounded down), and that creature takes the other half.

Rug of Smothering Damage Transfer:
While it is grappling a creature, the rug takes only half the damage dealt to it,
and the creature grappled by the rug takes the other half.

Shared semantic (no name dispatch):
While the source is attached to or grappling a target, incoming damage to the
source is split: source takes half (rounded down), target takes the remainder.

Next wiring: bind to existing on-hit / damage resolution primitives so the split
resolves in combat for both cards. Does not clear blockers or claim admission.
Exact-head CI required before any admission claim.
"""


def damage_transfer_notes() -> dict[str, object]:
    return {
        "semantic": "damage-transfer",
        "monsters": ["Cloaker", "Rug of Smothering"],
        "effect": "while attached/grappling, source takes half incoming damage (rounded down), target takes the other half",
        "source_verified": True,
    }

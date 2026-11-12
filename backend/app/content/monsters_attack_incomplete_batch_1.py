from __future__ import annotations

"""Foundation notes for 2014 attack:incomplete batch 1.

17 monsters remain in this category. Many share incomplete multi-weapon or
on-hit rider patterns already partially supported by the engine.

Targets for subsequent wiring:
- Balor (Longsword / Whip incomplete)
- Couatl (Bite / Constrict)
- Deva / Planetar / Solar (mace / bow incomplete)
- Djinni (Scimitar)
- Duergar (War Pick)
- Gray Ooze (Pseudopod)
- Lamia (Claws / Dagger)
- Mimic (Bite / Pseudopod)
- Oni (Claws / Glaive)
- Otyugh (Bite / Tentacle)
- Vampire / Vampire Spawn (Bite / Unarmed)

No admission claims. Exact-head CI required.
"""


def attack_incomplete_batch_1_targets() -> list[str]:
    return [
        "Balor",
        "Couatl",
        "Deva",
        "Djinni",
        "Duergar",
        "Gray Ooze",
        "Lamia",
        "Mimic",
        "Oni",
        "Otyugh",
        "Planetar",
        "Solar",
        "Vampire",
        "Vampire Spawn",
    ]

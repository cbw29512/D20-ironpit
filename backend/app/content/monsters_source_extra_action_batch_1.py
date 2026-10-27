from __future__ import annotations

"""Foundation notes for 2014 source:extra-action batch 1.

45 monsters remain in this category. Many are bonus actions, reactions, or
special actions already partially supported by the engine.

Targets for subsequent wiring (foundations only):
- Aboleth (Legendary actions / Enslave)
- Behir (Swallow)
- Chuul (Sense Magic)
- Cloaker (Phantasms / Moan)
- Darkmantle (Darkness Aura)
- Gelatinous Cube (Engulf)
- Ghost (Horrifying Visage)
- Giant Frog / Giant Toad (Swallow — related to #1066)
- Imp (Invisibility / Shapechanger)
- Roper (Grasping Tendrils / Reel)
- Rug of Smothering (Smother)
- Spectator (Eye Rays)
- Succubus/Incubus (Charm / Draining Kiss)
- Will-o'-Wisp (Consume Life / Ephemeral)

No admission claims. Exact-head CI required.
"""


def source_extra_action_batch_1_targets() -> list[str]:
    return [
        "Aboleth",
        "Behir",
        "Chuul",
        "Cloaker",
        "Darkmantle",
        "Gelatinous Cube",
        "Ghost",
        "Giant Frog",
        "Giant Toad",
        "Imp",
        "Roper",
        "Rug of Smothering",
        "Spectator",
        "Succubus/Incubus",
        "Will-o'-Wisp",
    ]

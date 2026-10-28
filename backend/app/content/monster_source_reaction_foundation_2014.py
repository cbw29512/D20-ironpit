from __future__ import annotations

"""Foundation for 2014 source:reaction semantic family.

Source-verified targets (not admitted):
- Shield Guardian: Shield reaction. When a creature makes an attack against the wearer of the guardian's amulet, the guardian grants a +2 bonus to the wearer's AC if the guardian is within 5 feet of the wearer.
  Existing Parry is self-AC bonus; this requires linked-ally AC bonus on incoming attack against ally. Bound trait (amulet wearer) is arena-neutral per existing audit.
- Spectator: Spell Reflection. If the spectator makes a successful saving throw against a spell, or a spell attack misses it, the spectator can choose another creature (including the spellcaster) it can see within 30 feet of it. The spell targets the chosen creature instead of the spectator. If the spell forced a saving throw, the chosen creature makes its own save. If the spell was an attack, the attack roll is rerolled against the chosen creature.
  New redirect semantics; not covered by existing parry/rock-catching/unnerving-mask.

Reuse existing universal reaction primitives where possible; extend for ally-target and spell-redirect without name dispatch.
No admission. Exact-head CI required.
"""


def source_reaction_targets() -> list[str]:
    return ["Shield Guardian Shield", "Spectator Spell Reflection"]

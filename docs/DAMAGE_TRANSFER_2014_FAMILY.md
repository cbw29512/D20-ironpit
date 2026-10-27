# 2014 Damage Transfer family

Source-verified from SRD 5.1:

- Cloaker: While attached to a creature, the cloaker takes only half the damage dealt to it (rounded down), and that creature takes the other half.
- Rug of Smothering: While it is grappling a creature, the rug takes only half the damage dealt to it, and the creature grappled by the rug takes the other half.

Universal primitive: when source has an active attachment or grapple on a specific victim, incoming damage to source is split (floor half to source, remainder to victim). Typed defenses apply independently. No name dispatch.

Reuses existing damage application and Grappled/attachment state. Python/browser parity required. Does not clear other blockers (attack:incomplete, etc.). Draft until exact-head CI.

Next: implement resolve_damage_transfer in shared damage pipeline, bind declarative flag on source cards, permanent tests, regenerate inventory.
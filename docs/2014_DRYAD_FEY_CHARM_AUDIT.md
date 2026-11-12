# 2014 Dryad Fey Charm — source and generic runtime audit

This is a **source-binding audit**, not a claim of 100% webpage-fight
certification. It must pass the exact-head Python, browser, roster, generated
artifact, hero and paired-edition gates before being merged.

## Printed ability facts

- **Action:** Fey Charm, one enemy humanoid or beast the Dryad can see
  within 30 feet, but only if the target can see the Dryad.
- **Save:** DC 14 Wisdom. Success grants that target source-specific
  immunity to the Dryad's Fey Charm for the next 24 hours (match-scoped).
- **Failure:** source-owned Charmed (not a controller/possession effect),
  lasting up to 24 hours, with no periodic end-of-turn save.
- **Capacities:** one humanoid **and** three beasts simultaneously; when a
  fresh save fails, the oldest prior target *of that type* is released.
  This release is not itself a successful save and grants no immunity.
- **Repeat:** a fresh Wisdom save when the Dryad or her allies harm the
  Charmed target. Standard Pit implements damage-triggered harm by comparing
  the original source's team and the damage-origin actor; this is not
  permission to trigger a repeat save when the target's own allies hit it.
  A successful repeat grants immunity; a failed repeat leaves Charmed.
- **Other exits:** owner death automatically releases the condition without
  immunity. Planar separation cannot occur in the locked arena. The optional
  Bonus Action voluntary dismissal is not selected by combat AI.
- **Controller:** the target is not under the Dryad's control, does not
  change sides, and is not forced to attack its own allies. Generic Charmed
  attack restrictions remain authoritative.

## Universal contract

The source card owns target types, save DC, duration, ability name and
capacity counts. The shared engine owns sight, saving throws, source-tagged
timed conditions, type-partitioned capacity, death/expiry, and source/ally
damage-triggered repeat saves. The browser uses those identical generic
fields. No Dryad-specific combat resolver.

Before calling this a fully accurate tabletop simulation, the broad phrase
"anything harmful" should be reviewed for **non-damage** harmful conditions
in the Iron Pit action engine. The above implementation covers harmful
damage events. Do not silently claim that all non-damage hostile actions
trigger extra repeat saves until that behavior is tested.

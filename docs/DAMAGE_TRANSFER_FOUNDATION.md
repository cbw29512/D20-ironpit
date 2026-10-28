# 2014 Damage Transfer foundation

Source-verified semantic family for attached damage share.

## Printed 2014 (Cloaker)
While attached to a creature, the cloaker takes only half the damage dealt to it (rounded down), and that creature takes the other half.

## Printed 2014 (Rug of Smothering)
While smothering a creature, the rug takes only half the damage dealt to it (rounded down), and the creature takes the other half.

## Semantic
When the owner is attached/grappling a specific target and takes damage, half (floor) is transferred to the attached creature as the same typed damage. No cycles. Reuse existing typed damage resolution. Attachment state from existing grapple/attach primitives.

## Status
Foundation only. Does not clear blockers or admit monsters. Exact-head CI required before any admission claim. Reuse existing damage and attachment primitives; no name dispatch.

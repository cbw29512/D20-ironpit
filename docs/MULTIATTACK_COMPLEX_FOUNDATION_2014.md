# 2014 multiattack:complex foundation

Source-verified from current catalog `srd_5_1_monsters_catalog.json` and generated blockers.

## Family (10 monsters)
Chuul, Gibbering Mouther, Kraken, Lamia, Vampire, Vampire Spawn, Werebear, Wereboar, Wererat, Weretiger.

## Existing primitives (reuse only)
- `multiattack-extra-attack` supported in inventory.
- Source-bound slots + `multiattack_binding` (e.g. Chuul grappled optional tentacles, Gibbering optional spittle).
- `multiattack_policy` with `at_most_once_attack_ids` (Vampire Spawn, Were* bite/tusks).
- Form-conditional attack ids already present (Humanoid/Hybrid/Boar/Rat form only).

## Source facts (no name dispatch)
- Printed Multiattack is one Action selecting legal printed alternatives under form and at-most-once constraints.
- Form availability is data on the attack, not a resolver branch.
- Optional secondary (tentacles/spittle) uses existing requirement/optional slot grammar.

## Status
Foundation only. Does not clear `multiattack:complex`, admit any monster, or claim Python/browser parity/exact-head CI.
Next: bind remaining policy/slots to existing sequence resolver; park form-switch interactions with Shapechanger until universal form primitive covers them.

Do not weaken fidelity. Exact-head CI required before any admission claim.

# Monk 5 shared hit-rider integration audit

Base: PR #485, `cbe23bd6525a18d8c7b6d9aba1d560e3f2ececf1`.

## Schema and state before execution

The immutable `ResourceBackedOnHitSaveRider` already supplies qualifying attack
IDs, save/DC, resource cost, condition timing, and successful-save modifiers.
Fresh combat state owns resources, `feature_last_turn_keys`, timed conditions,
and active modifiers. No new mutable state or source-specific resolver is needed.

The resolved weapon attack will expose its immutable `attack_id` separately from
the equipment `weapon_id`. This is resolver output, not audit-envelope inference.
The shared post-attack/reaction pipeline can then bind the existing rider from
the resolved hit, actual redirected target, and authoritative active-turn key.

## Findings and reuse

- FIX NOW: browser Multiattack appended a rider event before its triggering hit.
- FIX NOW: the rider was called from selected Action/Bonus Action wrappers;
  Opportunity Attacks and nested attack reactions bypassed those wrappers.
- Classification: ENGINE_EXISTS_BINDING_MISSING. Reuse the existing rider and
  shared damage-event sequencing in both engines, including zero-damage hits.
- Remove redundant wrapper calls so each hit gets one evaluation. Keep the
  once-per-turn guard tied to the active turn, including off-turn reactions.

RAW source: <https://www.dndbeyond.com/sources/dnd/br-2024/character-classes>,
Monk level 5. Stunning Strike is once per turn, not restricted to the Monk's turn.

## Parity and evidence

Python: resolved attack identity -> shared damage-event dispatch -> existing
resource-backed hit-save resolver. Browser: the equivalent dispatch chain.
Permanent regressions must exercise actual Extra Attack and Opportunity Attack
paths, event order, shared same-turn limits, and a different creature's turn.
Full Python/browser checks and exact-head CI are required before merge.

## Off-turn movement state extension

A successful-save Speed reduction must update remaining movement during the
active target's turn, preserving movement already spent. Add a reset-per-turn
`dash_uses_this_turn` counter (default 0, increment for each Dash grant) so a
Speed delta changes both the base allowance and every Dash allowance. The shared
hit-event adapter compares effective Speed before/after the rider and updates
remaining movement only for the active target. Grid movement must recheck the
current step's affordability after reactions, before committing the square.
This also requires source-level tests with no Dash, one Dash, and two Dashes.

Browser failed-save incapacitation must invoke existing Concentration cleanup
with every affected state immediately, matching the Python timed-condition path.

Dash source: <https://www.dndbeyond.com/sources/dnd/br-2024/rules-glossary>, Dash action. The reduced Speed also reduces Dash movement.

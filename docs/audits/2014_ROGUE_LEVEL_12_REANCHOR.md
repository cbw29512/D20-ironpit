# 2014 Rogue Level 12 Re-anchor Audit

Exact base: `main` `24a20f5a1dcdb30c36214fbe5b325d83f2430385`.

## State/schema first

The authoritative canonical-build policy requires one persistent 1-20 progression, deterministic combat-facing advancement choices, automatic derived-stat updates, and migration of pre-policy certified heroes to the canonical array/data-driven architecture **before their progression is extended further**.

Current `Mara Quickstep` 2014 source does not satisfy that migration prerequisite. `backend/app/content/rogue_thief_2014_profile.py` still starts from the legacy array `STR 8 / DEX 15 / CON 13 / INT 10 / WIS 12 / CHA 14`, applies 2014 Human `+1` to all six abilities, and carries hand-authored level 4/8/10 advancements. The current canonical policy instead defines the Rogue physical priority array as `DEX 15 / CON 14 / STR 13 / INT 10 / WIS 10 / CHA 10` for canonical mass-production builds.

## Level 12 RAW delta

Level 12 is an Ability Score Improvement level for the 2014 Rogue. The existing certified Mara progression reaches DEX 20 before level 12, so simply adding another `+2 DEX` is not legal under the normal 20 maximum. A different legal combat-facing ASI allocation or feat must therefore be selected for the canonical build.

## Existing-engine inventory

No new combat-engine primitive is justified by level 12 itself. The existing build/profile advancement schema already represents `AbilityIncrease` entries and recomputes final ability scores. Any resulting attack, AC, save, initiative, or HP changes must flow through the existing derived-stat/runtime compilation rather than a Rogue-specific resolver.

## Blocker

**Type:** canonical-content/architecture decision, not a missing combat primitive.

**Affected content:** 2014 Mara Quickstep level 12 and every later 2014 Rogue snapshot that must inherit the same canonical progression.

Two prerequisites block safe certification:

1. Migrate the already-certified 2014 Rogue progression to the current canonical array/data-driven architecture without silently changing established combat identity.
2. Choose the deterministic legal level-12 combat advancement after that migration. The current policy specifies optimization for the established role but does not provide a tie-break rule that uniquely determines the post-DEX-20 Rogue ASI/feat choice.

Per `AGENTS.md`, this must fail closed rather than guessing a feat or secondary ability allocation.

## Fastest safe resolution

Treat the migration as its own coherent tranche: preserve existing supported Rogue mechanics, convert Mara's build construction to the canonical progression architecture, prove levels 1-11 retain the intended certified combat behavior or explicitly document any required canonical-policy change, then resolve the first post-DEX-20 advancement choice in repository authority before implementing level 12.

Unrelated engine/certification work can continue while this content decision is parked.

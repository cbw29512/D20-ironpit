# D20 Iron Pit — single operational monster ability queue (2014 first)

## Current highest-yield remaining source blocker (2026-10-31)

- **Family:** source:trait Shapechanger (11 unbound after Imp/Quasit open PRs #1137/#1138/#1143).
- **Not in open PR for implementation:** remaining lycanthrope, Doppelganger, Mimic, Succubus, Vampire Shapechangers.
- **Next action:** source-verify each full paragraph against pinned 2014 text; classify as arena-neutral only when exact text proves movement/appearance-only with identical combat stats (reuse existing verified_arena_inert_trait_2014 pattern); fail-closed on mutation; no name dispatch; regenerate owned artifacts; Python/browser parity via existing form selection if combat-relevant. Do not admit until exact-head CI.
- **Open PR collisions:** #1103 Doppelganger foundation, #1137 Imp, #1138/#1143 Quasit. Independent of those.

## Shared on-hit single-save damage + timed condition — Quasit poison family

- **Verified source:** 2014 Quasit Claws (Bite in Beast Form): melee +4, 1d4+3 Piercing; one DC 10 Constitution saving throw after hit. Failed save applies **both** 2d4 Poison damage and Poisoned for ten rounds, with end-of-target-turn repeat saves; success negates both. The pinned typed row already contains these parameters.
- **Precise engine gap:** Current `SaveDamageEffectDefinition` and `SaveConditionEffectDefinition` are distinct alternatives; the 2014 source validators correctly reject the combined row. The next universal primitive must roll one save and atomically apply the ordered failed-save damage and timed condition, using existing typed damage and timed-condition lifecycle in Python/browser; never roll a second save or apply unconditional poison damage. This applies to other source-equivalent monsters and homebrew.
- **Regression:** `backend/tests/test_2014_quasit_composite_save_contract.py` locks the original source and fail-closed admission while wiring remains incomplete. This is blocker documentation/tests, **not** a completed combat resolver or monster admission.
- **Remaining independent Quasit obligations:** Scare, Invisible ends on Scare, Shapechanger source classification from PR #1138, and generated artifacts. Do not mark it battle-ready before full Python/browser tests and webpage fight.

## Generic source-owned Invisible self-buff exits — 2014 family

- **Implementation branch:** `feat/2014-source-invisibility-expiry-family` (ACTIVE). Same existing Invisible/concentration buff in Python/browser; printed source decides attack exit and optional spell-cast exit. No monster-name runtime decision or new condition.
- **Full 327-card source scan:** two fully supported source clauses: Sprite (attack or spell cast) and Imp (attack only). Quasit (using Scare) and Will-o'-Wisp (using Consume Life) remain unbound pending an exact generic named-action exit primitive; their clauses must never be weakened to spell casting.
- **Proof:** positive/negative source-mutating cases, renamed source, actual compiled Imp state and browser non-spell expiry regression. Generator-owned blocker and inventory artifacts synchronized on branch: Imp's `source:extra-action` is cleared; independent `source:trait` Shapechanger remains. **254/327** source-admitted and **73** blocked. Full exact-head CI still required; production locked.

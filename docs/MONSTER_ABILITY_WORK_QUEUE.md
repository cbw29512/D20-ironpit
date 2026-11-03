# D20 Iron Pit — single operational monster ability queue (2014 first)

## Shared on-hit single-save damage + timed condition — Quasit poison family

- **Verified source:** 2014 Quasit Claws (Bite in Beast Form): melee +4, 1d4+3 Piercing; one DC 10 Constitution saving throw after hit. Failed save applies **both** 2d4 Poison damage and Poisoned for ten rounds, with end-of-target-turn repeat saves; success negates both. The pinned typed row already contains these parameters.
- **Current status (2026-11-03):** Schema (`OnHitSaveDamage.failed_save_condition`), validation (`supported_composite_save_2014`), compiler, and Python hit-rider reuse of the single save for both damage and condition exist (see `attack_hit_riders.py`). Attack blocker clears for Quasit. Full 327-card family scan, browser parity proof, permanent multi-monster tests, and generated artifact regeneration remain for this focused PR. No admission claims.
- **Precise remaining:** Confirm browser serializer and resolution apply the condition from the shared save without a second roll; scan and bind all matching source cards; fail-closed on mutation.
- **Regression:** Existing `test_2014_quasit_composite_save_contract.py` and schema tests lock source. Extend for family.
- **Remaining independent Quasit obligations:** Scare, Invisible ends on Scare, Shapechanger source classification from PR #1138, and other source blockers. Do not mark battle-ready before full Python/browser tests and webpage fight.

## Generic source-owned Invisible self-buff exits — 2014 family

- **Implementation branch:** `feat/2014-source-invisibility-expiry-family` (ACTIVE). Same existing Invisible/concentration buff in Python/browser; printed source decides attack exit and optional spell-cast exit. No monster-name runtime decision or new condition.
- **Full 327-card source scan:** two fully supported source clauses: Sprite (attack or spell cast) and Imp (attack only). Quasit (using Scare) and Will-o'-Wisp (using Consume Life) remain unbound pending an exact generic named-action exit primitive; their clauses must never be weakened to spell casting.
- **Proof:** positive/negative source-mutating cases, renamed source, actual compiled Imp state and browser non-spell expiry regression. Generator-owned blocker and inventory artifacts synchronized on branch: Imp's `source:extra-action` is cleared; independent `source:trait` Shapechanger remains. **254/327** source-admitted and **73** blocked. Full exact-head CI still required; production locked.

# D20 Iron Pit — single operational monster ability queue (2014 first)

## Shared on-hit single-save damage + timed condition — Quasit poison family — IMPLEMENTED

- **Verified source:** 2014 Quasit Claws (Bite in Beast Form): melee +4, 1d4+3 Piercing; one DC 10 Constitution saving throw after hit. Failed save applies **both** 2d4 Poison damage and Poisoned for ten rounds, with end-of-target-turn repeat saves; success negates both. The pinned typed row already contains these parameters.
- **Universal primitive:** `SaveDamageEffectDefinition.failed_save_condition` (and `OnHitSaveDamage.failed_save_condition`) carries the ordered timed condition. Python (`attack_hit_riders.py`) and browser (`browser-attack.js`) resolve the damage save once and pass the identical `(roll, succeeded)` pair into the existing condition lifecycle. No second save is rolled; success negates both. Source validators accept the composite row via `supported_composite_save_2014`.
- **Evidence:** compilation test `backend/tests/test_2014_quasit_composite_compilation.py`; contract test `backend/tests/test_2014_quasit_composite_save_contract.py`; new runtime parity test `backend/tests/test_2014_composite_save_runtime.py` and browser smoke `frontend/browser-composite-save-runtime.test.cjs`. Quasit is source-admitted (not listed in `MONSTER_BLOCKERS_2014.md`). Remaining independent obligations (Scare, Invisible-on-Scare, Shapechanger) stay blocked; no whole-monster battle-ready claim.
- **Admission:** 257/327 unchanged by this primitive (already source-cleared). Production remains locked.

## Generic source-owned Invisible self-buff exits — 2014 family

- **Implementation branch:** `feat/2014-source-invisibility-expiry-family` (ACTIVE). Same existing Invisible/concentration buff in Python/browser; printed source decides attack exit and optional spell-cast exit. No monster-name runtime decision or new condition.
- **Full 327-card source scan:** two fully supported source clauses: Sprite (attack or spell cast) and Imp (attack only). Quasit (using Scare) and Will-o'-Wisp (using Consume Life) remain unbound pending an exact generic named-action exit primitive; their clauses must never be weakened to spell casting.
- **Proof:** positive/negative source-mutating cases, renamed source, actual compiled Imp state and browser non-spell expiry regression. Generator-owned blocker and inventory artifacts synchronized on branch: Imp's `source:extra-action` is cleared; independent `source:trait` Shapechanger remains. **254/327** source-admitted and **73** blocked. Full exact-head CI still required; production locked.

## Source-only Etherealness movement — 2014 cross-roster family

- **Scope:** All 327 pinned cards scanned. Three complete printed `Etherealness` actions (Ghost, Night Hag, Succubus/Incubus) are verified as exclusively entering or leaving the Ethereal Plane, with source-specific visibility/heartstone restrictions. This is a general full-clause source proof, not monster-ID dispatch.
- **Locked Pit policy:** entering the Ethereal Plane is unavailable; the printed actions remain on immutable cards, but create no fight-local planar state, saves, damage, buffs or resources. If a future card adds an in-combat rider, the proof fails closed; no invented magical effect.
- **Obligations cleared:** three extra-action source obligations, not three fully admitted monsters. Their other printed combat effects remain blocked and no admission increase is claimed. Do not alter generated reports manually. Pending CI/exact-head verification and production stays locked.

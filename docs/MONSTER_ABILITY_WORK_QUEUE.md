## 2014 Frog: intentional arena-neutral (no combat actions)

- Source-verified: Amphibious (breathing) and Standing Leap (jump distances) are arena-inert under Pit contract (no water context, movement modes preserved but no outcome change in standard grid fights without special terrain).
- No attacks or actions. Classified arena:neutral by design; non-runnable. Existing tests confirm. No admission. Production locked.
- Next independent family: remaining source:trait or mechanic:spellcasting not in open PRs.

# D20 Iron Pit — single operational monster ability queue (2014 first)

## Generic source-owned Invisible self-buff exits — 2014 family

- **Implementation branch:** `feat/2014-source-invisibility-expiry-family` (ACTIVE). Same existing Invisible/concentration buff in Python/browser; printed source decides attack exit and optional spell-cast exit. No monster-name runtime decision or new condition.
- **Full 327-card source scan:** two fully supported source clauses: Sprite (attack or spell cast) and Imp (attack only). Quasit (using Scare) and Will-o'-Wisp (using Consume Life) remain unbound pending an exact generic named-action exit primitive; their clauses must never be weakened to spell casting.
- **Proof:** positive/negative source-mutating cases, renamed source, actual compiled Imp state and browser non-spell expiry regression. Generator-owned blocker and inventory artifacts synchronized on branch: Imp's `source:extra-action` is cleared; independent `source:trait` Shapechanger remains. **254/327** source-admitted and **73** blocked. Full exact-head CI still required; production locked.

## Source-only Etherealness movement — 2014 cross-roster family

- **Scope:** All 327 pinned cards scanned. Three complete printed `Etherealness` actions (Ghost, Night Hag, Succubus/Incubus) are verified as exclusively entering or leaving the Ethereal Plane, with source-specific visibility/heartstone restrictions. This is a general full-clause source proof, not monster-ID dispatch.
- **Locked Pit policy:** entering the Ethereal Plane is unavailable; the printed actions remain on immutable cards, but create no fight-local planar state, saves, damage, buffs or resources. If a future card adds an in-combat rider, the proof fails closed; no invented magical effect.
- **Obligations cleared:** three extra-action source obligations, not three fully admitted monsters. Their other printed combat effects remain blocked and no admission increase is claimed. Do not alter generated reports manually. Pending CI/exact-head verification and production stays locked.

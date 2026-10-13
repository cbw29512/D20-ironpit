# Technical debt cleanup note

Updated 2026-10-13. Docs-only. No runtime, rules, or certification changes.

## What this records

- Current authoritative sources remain `docs/MONSTER_ABILITY_WORK_QUEUE.md`, the generated `docs/MONSTER_BLOCKERS_2014.md`, and `docs/UNIVERSAL_MECHANIC_INVENTORY.md`.
- Draft PR #762 (`feat/2014-incoming-hit-save-reaction`) is the preferred foundation for Stone Giant Rock Catching and other incoming-hit save-negation Reactions. Do not start a second implementation.
- `docs/MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md` is not on current main. It exists only on the unmerged PR #680 commit (`88881607`). Source cards and the generated blocker report outrank it.
- Historical `docs/*_AUDIT*.md` files are evidence of past gates. They are not the live cursor. Old Actions run URLs in those files will age out; they are informational only.
- Legacy modules `backend/app/content/legacy_monster_roster.py` and `backend/app/content/legacy_migrated_monsters.py` are still imported. They are not dead code. Migrate callers before any removal.
- No monster-name combat routing was found in the live Python or browser engines.

## What remains

1. Finish and merge #762, then bind source parameters for Stone Giant (and any other one-blocker reaction consumers).
2. Death-burst family (Balor Death Throes, Mephit Death Burst, etc.) as one universal on-death primitive.
3. Archive or clearly banner superseded audit docs once their outcomes are fully reflected in the queue and generated manifests.
4. Continue the approved 2014 monster queue without inventing new mechanics.

## Out of scope for this note

Gameplay changes, card edits, Netlify deploy, and any alteration of certified counts.

## TODO

- [ ] Before merging this docs PR, re-check whether it is still needed (confirm #762 status, whether the blueprint clarification is still accurate, and whether any newer queue update already covers this note).

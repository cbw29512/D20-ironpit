# Iron Pit Roadmap

## P0 — Prove the actual game

- Exact-head CI green.
- Static browser combat only; no production API dependency.
- 1–8 hero cards vs. 1–8 monster cards.
- Standard 30-foot Pit and optional 5-foot already-engaged start.
- Every combatant closes toward melee; nobody kites or retreats.
- Legal ranged/thrown attacks can be used while closing.
- Full legal Multiattack/Extra Attack resolves before remaining movement closes the gap.
- Fight continues until one side is dead, not merely at 0 HP.
- Unconscious player characters, Death Saving Throws, damage at 0 HP, massive damage, and finishing attacks resolve correctly.
- Selected combatants replay as stick figures with HP, movement, attacks, hits, criticals, healing, downed/dead states, and a final result.
- Browser and Python reference behavior remain covered by deterministic regression tests.

## P1 — Unlock more RAW combatants through reusable mechanics

Implement outcome-changing mechanics as engine capabilities before marking dependent cards RAW-ready:

- general saving throws;
- Grappled;
- Restrained;
- broader condition support;
- save-based damage/condition riders;
- reactions that can change combat outcome;
- recharge actions;
- poison and similar riders;
- forced movement/pushback interactions that return to the close-and-brawl policy;
- spell slots, concentration, spell attacks, and saving-throw spells after the martial/monster foundation is stable.

## P1 — Expand representative hero coverage

Prioritize a small set that proves distinct combat behavior before attempting the full 720-card plan:

- Fighter;
- Barbarian;
- Rogue;
- Ranger;
- Cleric;
- Wizard;
- then the remaining core classes.

Each runnable build must have the class features, resources, attacks, defenses, and action economy that can affect its Pit result.

## P2 — Resume monster expansion

- Keep the full 330 SRD 5.2.1 catalog available for browsing.
- Promote monsters to RAW-ready only in mechanic-compatible audited batches.
- Preserve exact source/license metadata.
- Never increase the ready count by ignoring an outcome-changing feature.

## P2 — Presentation polish

- Improve class/monster-specific stick silhouettes and weapon animation families.
- Add clearer round pacing and optional replay speed controls.
- Improve target/hit/death readability for 8-vs-8 fights.
- Preserve reduced-motion support.
- Keep the detailed rules log secondary to the watchable fight.

## P3 — Persistence and social/product features

Accounts, battle history, rankings, tournaments, cosmetics, and other persistence features come only after the combat/watch loop is excellent and mechanically trustworthy.

Anything involving money, prizes, wagering, crypto, or cash-value predictions requires a separate product/legal review and is not part of the combat roadmap.

# Iron Pit — RAW rules first, cards second, combat by composition

Decision locked 2026-10-23. This is an implementation and acceptance contract, not a new engine rewrite mandate. Read with [SOUL](../SOUL.md), [Universal Card-to-Combat Contract](UNIVERSAL_CARD_COMBAT_CONTRACT.md), [Implementation Playbook](IRON_PIT_IMPLEMENTATION_PLAYBOOK.md), and [locked rules](IRON_PIT_LOCKED_RULES.md). Those existing specifications remain authoritative for individual mechanics.

## Design rule

Build each RAW 2014 combat rule as a **source-neutral, reusable primitive** before admitting cards which use it. Reuse those same primitives for 2024, monsters, pregens and homebrew with edition-qualified parameters. A completed immutable card is a *form of facts* (AC, HP, stats, attacks, effects, triggers, constraints, uses and durations), not a program. The universal engine reads facts, rolls dice, compares totals, resolves declared effects and logs numerical outcomes. Creature names and printed ability labels are for display/logging, never control flow.

For a supported card, admission must require **zero new runtime combat branches**: compile form -> validate capabilities -> fresh fight state -> roll/compare -> resolve shared typed effect chain -> log -> repeat until defeat. The only legitimate reason to add new engine behavior is a *new semantic rule* that cannot be represented by existing primitives; implement it once with neutral parameters and paired Python/browser tests, then batch every card sharing that signature.

## Implementation decision tree (mandatory for every blocked card)

1. Read printed 2014 source card verbatim. Break each ability into **trigger, eligibility, economy, attack/save/check, damage/healing, conditions, resource, duration, exit and logging**. Keep the source card immutable.
2. Map each clause to an **existing** semantic primitive and its browser/Python implementations. Inspect existing PRs, source bindings, generated reports and tests before writing code.
3. If all clauses map, **only change the source-to-card adapter / declarative form**. Do not edit the combat runtime. Add source binding and a renamed-card (no name dispatch) test.
4. If one clause is not supported, implement exactly one **universal semantic primitive**, parameterized for all matching cards; test both engines. Do not smuggle card IDs into runtime.
5. If some nonmovement clauses are unimplemented, remain blocked. Never admit on partial ability support or declare an arena-neutral feature without a documented source/arena proof.
6. Update the generated blocker list via its script, then run source, Python, browser, hero, paired-edition, and actual webpage-fight checks as applicable. Count an admission **only** with certified evidence. Start the next blocker family immediately.

## Iron Pit forced movement: no more feature work

All involuntary push/pull/drag/shove displacement is a **no-op positional effect** at the universal engine policy boundary. Source distances, checks and saves may be logged but x/y do not change. **Damage, Prone, grapple, restraint, other effects, costs, and timing remain operative.** Voluntary movement still follows separate arena rules. Never add a pathfinding or relocation algorithm to satisfy printed forced movement. Do not mark Whirlwind/Whelm/Engulf or a charge ability fully implemented merely because movement is ignored.

## Measurable output — stop cycling through planning

Use **2014 source-admitted and separately browser-fight-certified** card counts, with exact main SHA and evidence. Baseline taken from generated report when this decision was written: 239 / 327 source-admitted, 88 blocked; regenerate before making progress claims. Goal: one independently certified capability batch per PR; reduce blockers, not increase commit count. If CI fails, report the **failing check and reproducible assertion**, repair it before unrelated changes. A GitHub failure status without accessible logs is insufficient evidence to guess at a regression; restore observability or reproduce locally.

## First bounded work batch

- Check the existing Hydra variable-head schema, parser, timing, end-turn regrowth, source trait naming, browser serialization and reaction accounting. Existing universal lifecycle code **must be reused**, not rewritten.
- Resolve only genuinely missing binding/validation details, certify it, regenerate blockers and record any true admission delta.
- Next, resolve Rust Monster and Sea Hag extra Actions using shared action/effect grammar; batch remaining identical mechanics across cards.
- Treat PR #1032 forced-movement work separately; merge only after exact-head CI green. Keep Netlify production locked.

## Required review evidence

Every claimed completed monster must link: immutable source card -> typed compiled form -> shared mechanics used -> Python and browser parity tests -> generated roster change -> passing exact-head CI -> real webpage-fight check. A card whose source admission passes but browser encounter is unverified must be explicitly labeled *source-admitted, not combat-certified*.

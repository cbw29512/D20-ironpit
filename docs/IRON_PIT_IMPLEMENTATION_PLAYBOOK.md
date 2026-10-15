# Iron Pit — execution manual

**One process. One authority per concern. No stale progress claims.** Read [SOUL](../SOUL.md) for architecture, [document map](DOCUMENTATION_MAP.md) for document status, and the [locked rules index](IRON_PIT_LOCKED_RULES.md) only when the touched behavior needs a product decision. Exact source, current tests, generated reports and exact-head GitHub Actions determine implementation truth.

## Start here — each session

1. Fetch the exact `main` SHA, changed files and open PR heads. Inspect [subsystem ownership](TWO_AGENT_COORDINATION.md) before any edits. Don't duplicate a live PR.
2. For monster work, start at the [canonical queue](MONSTER_ABILITY_WORK_QUEUE.md), reconcile with the [generated 2014 blockers](MONSTER_BLOCKERS_2014.md) and [mechanic inventory](UNIVERSAL_MECHANIC_INVENTORY.md). Do **not** treat dated historical tables as live counts.
3. Select **one lane**: [Monsters](playbooks/MONSTERS.md), [Pregens](playbooks/PREGENS.md), or [Universal engine](playbooks/UNIVERSAL_ENGINE.md). Read only its precise source/card, nearest equivalent Python/browser resolver, serializer and permanent tests.
4. Declare branch, subsystem, source baseline, expected files and one family deliverable. If another active PR owns it, reconcile that PR instead of opening a parallel implementation.
5. Implement, verify and merge the family; measure the resulting change in exact source obligations and certified cards. Continue with the next **unblocked** family.

## Card → universal engine contract

An immutable card declares printed name, edition, AC/HP, DC, attack/damage dice, typed damage, target/range/area, trigger, action cost, resource, recharge, duration and exit/reset qualifiers. The engine owns attack/save rolls, conditions, typed damage defenses, healing, action economy, geometry, lifecycle and audit. **Printed names are source/log labels, never runtime behavior switches.**

Map the exact ability to `trigger → eligibility → action/resource → attack/check/save → ordered typed effects → fight state → expiration/reset → audit`. Search monsters **and** pregens before creating a primitive; compose existing capabilities first. Preserve 2014/2024 source separation. Unsupported outcome-changing effects fail closed; park the single blocker and keep moving. Detailed acceptance: [universal card contract](UNIVERSAL_CARD_COMBAT_CONTRACT.md).

## One family / one certification loop

1. Source-proof exact printed behavior; map immutable schema, temporary per-fight state, Python oracle, browser production resolver, serializer, logs and independent parity tests.
2. Implement a reusable semantic family and bind every matching card. Include an unrelated synthetic-card/homebrew equivalence test for a new/widened primitive. No fake admissions or monster-specific dispatch.
3. Run **focused** tests while editing. Remove stale helpers/imports and duplicate calculations in the touched subsystem. Re-generate the owning artifacts **once** on the intended final branch head.
4. Require the repository's applicable 2014 Basic Roster, Hero, Paired Edition, source/generated parity, Python and browser CI gates green on the **exact same head SHA**. An intermediate-head green result is not certification.
5. Merge, refresh actual generated blockers/inventory, and compare before/after `(monster, printed ability)` obligations and admitted monsters. Record any remaining gap in the existing queue, **not** another tracker. The production Netlify lock stays on.

## Verification vocabulary

- **Implemented:** code exists at a named commit.
- **Tested:** the relevant checks ran on that commit.
- **CI green:** every applicable required job completed successfully on the exact head.
- **Source-admitted:** the generated classifier accepted the source card; not proof of every fight.
- **Runtime certified:** independent manifests and Python/browser gates agree.
- **Unverified:** say so explicitly; do not transfer stale PR-head evidence.

Deep rules and product exceptions remain in [Iron Pit Rules Contract](IRON_PIT_RULES_CONTRACT.md), [universal combat architecture](UNIVERSAL_COMBATANT_ARCHITECTURE.md), [historical battlefield design reference](VTT_CARD_BATTLEFIELD_CONTRACT.md) (current Pit rules supersede it), and [main action selection](MAIN_ACTION_SELECTION_CONTRACT.md). Never rewrite those decisions from a cleanup prompt.

# 2024 Fighter Level 18 — Survivor Engine Inventory

## Authoritative RAW

Source: D&D Beyond Basic Rules 2024, Fighter → Champion → Level 18: Survivor (also published in SRD 5.2).

Survivor has two independent combat-relevant benefits:

1. **Defy Death** — advantage on Death Saving Throws; a natural 18–20 on a Death Saving Throw gains the benefit of rolling a natural 20.
2. **Heroic Rally** — at the start of each turn, regain HP equal to 5 + Constitution modifier when Bloodied and at least 1 HP.

The Fighter class table adds no separate level-18 base-class feature beyond the subclass feature. Existing level-17 Action Surge, Indomitable, Second Wind, Weapon Mastery, Studied Attacks, and Superior Critical must remain inherited unchanged.

## Existing universal-engine inventory

### Heroic Rally

`data/combat_engine_coverage_v1.json` currently marks `regeneration` **unsupported** with the blocker: `No universal conditional start-turn regeneration primitive is certified.`

Monster content already carries a generic `regeneration` data field (`backend/app/content/monster_source_2014.py`) and the 2014 candidate classifier recognizes it. This is strong evidence that Survivor must not receive a Fighter-name special case. The correct implementation is a reusable conditional start-of-turn healing primitive that can later unlock monster regeneration as well.

Required semantics for the reusable primitive:

- trigger: start of creature turn;
- amount: data-driven fixed/base amount plus optional ability modifier;
- HP predicate: data-driven threshold (Survivor uses Bloodied / at or below half maximum HP);
- minimum-current-HP predicate: Survivor requires at least 1 HP;
- cap healing at maximum HP;
- emit structured combat logging for trigger, amount, before/after HP, and source feature;
- Python/browser behavior must be equivalent;
- certification coverage must prove the primitive rather than bypassing it.

### Defy Death

No existing repository search result exposes a certified generic Death Saving Throw capability. This must be treated as **missing until proven otherwise**, not inferred from ordinary saving-throw advantage.

Required reusable semantics:

- generic Death Saving Throw resolver/state, not Fighter-specific code;
- data-driven advantage on death saves;
- data-driven natural-roll success upgrade range (Survivor: 18–20 behaves as natural 20);
- preserve ordinary natural-1/natural-20 death-save semantics;
- structured logging of dice, advantage source, natural result, upgraded result, and death-save state transition;
- Python/browser parity and permanent tests.

## Decision

**Do not register or certify Karnok L18 yet.** Level 18 introduces genuinely missing universal engine behavior. READY must be earned only after both Survivor halves are implemented and exercised through the normal certification path.

The fastest safe implementation order is:

1. implement/test generic conditional start-turn regeneration and reuse the existing monster-facing regeneration data concept where schemas can be shared safely;
2. implement/test generic Death Saving Throw state/resolution and configurable Survivor modifiers;
3. add browser parity and structured logs for both;
4. build the L18 canonical profile using data declarations only;
5. run canonical/build/combat/resource audits and certification generation;
6. add permanent CI regressions and only then allow the generated manifest to advance.

## Edition separation

Do not reuse 2014 Champion Survivor semantics as the 2024 declaration. 2014 Survivor has start-turn healing but does not contain the 2024 Defy Death benefit. The universal primitives may be shared; edition-specific feature data must remain separate.

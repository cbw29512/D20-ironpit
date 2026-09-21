# 2024 Fighter Level 18 — Survivor Engine Inventory

## Authoritative RAW

Source: D&D Beyond Basic Rules 2024, Fighter → Champion → Level 18: Survivor (also published in SRD 5.2).

Survivor has two independent combat-relevant benefits:

1. **Defy Death** — advantage on Death Saving Throws; a natural 18–20 on a Death Saving Throw gains the benefit of rolling a natural 20.
2. **Heroic Rally** — at the start of each turn, regain HP equal to 5 + Constitution modifier when Bloodied and at least 1 HP.

The Fighter class table adds no separate level-18 base-class feature beyond the subclass feature. Existing level-17 Action Surge, Indomitable, Second Wind, Weapon Mastery, Studied Attacks, and Superior Critical must remain inherited unchanged.

## Corrected universal-engine inventory

The first inventory pass was fail-closed, but repository inspection found existing equivalent capabilities that must be reused rather than rebuilt.

### Heroic Rally — existing equivalent capability

`backend/app/combat/survivor.py` already implements the required start-turn Survivor healing semantics through `survivor_heal_amount`: positive HP, Bloodied (`current_hp * 2 <= maximum`), and healing capped at effective maximum HP. The shared start-turn path already invokes it.

Browser parity exists in `frontend/browser-state.js`, with permanent coverage in `frontend/browser-survivor.test.cjs`. The 2014 Champion runtime already compiles its edition-specific Survivor amount into the same neutral runtime field.

**Decision:** do not add a second regeneration primitive merely to rename this behavior. For 2024 Heroic Rally, compile the edition-specific `5 + Constitution modifier` value into existing `survivor_heal_amount`. Keep 2014 and 2024 declarations separate while reusing equivalent runtime behavior.

Monster `regeneration` remains a separate certification concern because monster regeneration can carry suppression conditions Survivor does not model. Do not broaden this Fighter change into monster regeneration unless later inventory proves semantic equivalence.

### Defy Death — existing Death Save engine, one genuine gap

`backend/app/combat/death_saves.py` already provides the generic Death Saving Throw state/resolver, ordinary natural-1/natural-20 behavior, success/failure accumulation, stabilization, death, structured `BattleEvent` output, and error-first logging.

`backend/app/combat/defensive_modifier_rules.py` already provides data-driven Death Save advantage through `ModifierKind.DEATH_SAVE_ADVANTAGE` and `death_save_advantage_sources()`. Defy Death therefore does **not** justify a second resolver or Fighter-specific advantage branch.

The genuine missing reusable capability is only the **natural-roll upgrade threshold**: a data-driven way for a feature to make a configured natural range (2024 Survivor: 18–20) receive the existing natural-20 Death Save result.

Required semantics:

- default threshold remains natural 20 so existing content is unchanged;
- threshold is data-driven and reusable, never keyed to Fighter/Karnok/Survivor names;
- 2024 Survivor declares threshold 18 and Death Save advantage through edition-specific feature data;
- natural 1 remains two failures;
- qualifying 18–20 results reuse existing `restore_hit_points(state, 1)` behavior;
- Python and browser Death Save paths agree;
- events preserve the actual natural die while describing the feature upgrade;
- permanent tests cover default 20, upgraded 18/19/20, advantage selection, natural 1, and edition isolation.

## Revised implementation order

1. Reuse `survivor_heal_amount` for 2024 Heroic Rally; do not duplicate healing architecture.
2. Add the smallest reusable data declaration for Death Save natural-20-result threshold, defaulting to 20.
3. Teach the existing Python Death Save resolver to consume it.
4. Add equivalent behavior to the existing browser Death Save path.
5. Add Python/browser regressions proving ordinary Death Saves are unchanged and 2024 Defy Death works.
6. Build Karnok L18 using edition-specific data declarations only.
7. Run canonical/build/combat/resource audits and generated certification; READY advances only if those gates pass.

## Edition separation

2014 Champion Survivor may continue using shared `survivor_heal_amount`, but it must not receive 2024 Defy Death. The reusable Death Save threshold defaults to 20 and only the 2024 L18 declaration may lower it to 18. Shared runtime primitives are allowed; RAW declarations remain hard-separated by edition.

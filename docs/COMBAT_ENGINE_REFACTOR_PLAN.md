# Iron Pit Combat Engine Refactor Plan

This document is the implementation plan for completing the Iron Pit combat engine and the canonical 2024 SRD monster roster. It supplements `IRON_PIT_RULES_CONTRACT.md`; if the two disagree, the rules contract wins.

## Why this refactor exists

The current engine has proven reusable primitives, but development reached them too reactively: a monster exposed a missing mechanic, the engine gained a partial capability, browser/runtime parity had to catch up, and certification then exposed the next gap. That produced too much churn.

The refactor changes the build order from **monster -> missing rule -> patch** to **complete combat-mechanic inventory -> canonical combat IR -> universal resolver families -> compile all content -> certify**.

The current certified roster is a regression baseline, not a design boundary. Already-correct mechanics must be preserved while duplicated representations, parser/runtime coupling, and manual browser dependency wiring are removed.

## Non-negotiable invariants

1. D&D 2024 / SRD 5.2.1 is the current certification authority.
2. Monsters and pregens are both combatants. Equivalent RAW behavior uses the same primitive.
3. Names are labels, never behavior selectors.
4. Runtime never parses English source text.
5. Source text compiles to validated immutable combat data before certification.
6. Unsupported outcome-changing semantics fail closed.
7. Step, Watch, Replay, and Turbo consume the same event/resolution path.
8. Python is the certification oracle; browser behavior must remain equivalent.
9. Weapon mastery is permission-gated: the combatant must use the weapon and have mastery for that exact weapon before the weapon's mastery property can activate.
10. Production files have a hard 150-line cap; ~130 lines is the extraction warning.
11. No monster-name, class-name, spell-name, or weapon-name runtime branches when immutable data can represent the behavior.
12. Do not promote content because a parser recognizes words; promote only when source -> IR -> runtime -> browser -> audit is complete.

## Target architecture

```
SRD source / canonical build data
             |
             v
      source compiler
             |
             v
     canonical combat IR
             |
   +---------+----------+
   |                    |
Python interpreter   Browser interpreter
   |                    |
   +---------+----------+
             |
       canonical events
             |
   Step / Watch / Replay / Turbo
```

The combat IR is a small D&D combat language. Content should normally differ only by immutable parameters.

### Canonical combatant

A single combatant concept owns combat-facing data:

- stats, AC, HP, speed, size, position;
- defenses, resistances, vulnerabilities, immunities;
- conditions and condition immunities;
- actions and action costs;
- resources and resource recovery;
- equipment, proficiencies, and weapon masteries;
- spellcasting data;
- traits/features expressed through universal capabilities;
- tactical policy data separate from RAW legality.

Monster/pregen identity is metadata, not a resolver fork.

### Canonical action shape

Every combat action should converge toward these concepts:

- identity/label;
- action cost (`action`, `bonus_action`, `reaction`, etc.);
- legal trigger/timing;
- targeting/geometry/range;
- resource requirements/cost;
- resolution (`attack_roll`, `saving_throw`, automatic/legal effect, check);
- ordered effects;
- source/audit metadata.

Existing working models are migrated toward this shape; do not create a second parallel engine and leave both active indefinitely.

### Universal effect families

The target effect vocabulary includes at least:

- damage;
- healing;
- temporary HP;
- condition apply/remove;
- forced movement;
- speed/movement modification;
- attack/save/defense modifiers;
- resource spend/restore/recharge;
- repeat save / escape;
- transformation/form change;
- summon/created combatant where in-scope;
- position/teleport where in-scope;
- triggered follow-up effects.

Complex abilities are compositions of these primitives plus timing/eligibility data.

### Universal trigger/timing vocabulary

Timing is centralized rather than reimplemented per feature. Required event points include, as needed by RAW:

- combat/round/turn start and end;
- before action / after action;
- before attack / attack roll / on hit / after hit;
- before damage / on damage / after damage;
- movement start / leaves reach / enters range;
- condition applied/removed;
- resource spent/restored;
- zero HP/death-state transitions.

Source-defined duration and eligibility (`once_per_turn`, `until_target_turn_end`, repeat save timing, etc.) are immutable data.

## Refactor phases

### Phase 0 - Freeze and measure

- Preserve all currently certified monsters as regression fixtures.
- Record exact-head certification, blocker families, capability coverage, generated parity, Python/browser gate state.
- Do not hand-edit generated readiness manifests.

**Gate:** baseline is reproducible from repository generators.

### Phase 1 - Complete combat-mechanic inventory

Inventory every outcome-changing mechanic in the canonical 330-monster 2024 corpus, plus core combat rules needed by those mechanics. Use 2014 material only as an architectural stress test; never mix editions in certification.

Every detected mechanic receives:

- canonical mechanic family;
- source examples/variants;
- affected monster count;
- engine status: `supported`, `partial`, `missing`, or `arena_out_of_scope`;
- parser status;
- Python runtime status;
- browser runtime status;
- audit status;
- dependencies;
- next reusable primitive needed.

**Gate:** every blocker in the 330 roster maps to a known mechanic family or an explicit unclassified-source defect. No broad `planned` bucket without a concrete family.

### Phase 2 - Normalize the combat IR

Map existing action, save, attack, control, resource, and capability models to one canonical action/effect vocabulary.

Rules:

- preserve already-correct runtime behavior;
- migrate incrementally with adapters only while needed;
- each adapter has a removal target;
- no new mechanic may add another parallel representation;
- schema first, resolver second.

**Gate:** ordinary attacks, save-damage actions, conditions, forced movement, Recharge, and currently certified mechanics round-trip through canonical IR without source-fidelity loss.

### Phase 3 - Separate rules legality from tactical AI

Rules engine answers what is legal and what it does. Tactical policy chooses among legal actions.

- no RAW inside monster-name AI branches;
- tactical choices may use position, expected damage, resource state, initiative, target state, and explicit policy data;
- opening-only abilities obey the Iron Pit initiative rule where the contract requires it.

**Gate:** changing tactical policy cannot change rules interpretation.

### Phase 4 - Centralize timing, conditions, resources, and reactions

Finish universal lifecycle primitives before more named content work:

- condition consequences and duration;
- repeat saves and escape/removal;
- once-per-turn/round limits;
- Recharge and limited uses;
- bonus actions;
- reactions/opportunity attacks;
- triggered effects;
- concentration where required by supported spells.

**Gate:** a mechanic applied by a monster, pregen, spell, item, or weapon reaches the same resolver path.

### Phase 5 - Browser module/runtime cleanup

Stop maintaining behavior through fragile global script load order.

Target:

- explicit module imports/dependencies;
- production and tests use the same dependency graph;
- generated content is data, not executable monster logic;
- browser interpreter consumes the same canonical IR semantics as Python.

Until module migration is complete, CI must batch-detect missing browser harness dependencies before browser regression execution.

**Gate:** extracting a helper cannot cause one-test-at-a-time missing-global failures.

### Phase 6 - Split readiness dimensions

Certification reports distinguish:

- `rules_ready`: all outcome-changing RAW compiled and audited;
- `presentation_ready`: required figure/UI metadata exists;
- `production_ready`: rules + browser parity + presentation + permanent tests/gates.

Only `production_ready` is public-ready. Presentation defects must not masquerade as missing combat semantics.

**Gate:** blocker reports identify the actual failing layer.

### Phase 7 - Finish monsters by mechanic yield

Implement remaining mechanic families in descending useful yield, not alphabetically and not one monster at a time.

For each family:

1. inventory all RAW variants;
2. define/extend immutable schema;
3. implement one universal resolver;
4. implement browser parity;
5. compile all compatible monsters;
6. source-audit the whole family;
7. regenerate all 330;
8. promote only genuinely unblocked monsters;
9. run milestone preflight once the tranche is complete.

Current high-yield families include save/complex actions, conditions/control, traits, limited-use mechanics, spellcasting, bonus actions, legendary actions, and reactions. Exact ordering must come from the Phase 1 inventory, not stale counts in this document.

**Gate:** every completed family has no known compatible source still blocked solely because that family was not compiled.

### Phase 8 - Production hardening

- remove migration adapters and legacy duplicate fields;
- refactor touched ~130+ line modules before adding behavior;
- eliminate hand-maintained generated duplicates;
- verify deterministic Replay and full-mechanics Turbo;
- verify audit logs preserve RAW decision evidence;
- exact-head CI fully green.

**Gate:** 330/330 canonical 2024 SRD monsters are production-ready or any remaining item has an explicit user-approved product-scope exception.

### Phase 9 - Pregens

Only after the monster engine is complete enough for the canonical roster, compile pregens through the same combat IR and resolver primitives. Pregen work may require new RAW mechanics, but those mechanics are added universally and immediately become available to monsters/homebrew too.

## Definition of done

The refactor is complete when:

- one universal combat engine handles monsters and pregens;
- every outcome-changing mechanic in the canonical 2024 monster corpus is classified;
- every supported mechanic has Python/browser parity and source-audit coverage;
- runtime content is immutable structured data rather than name-driven code;
- the public 2024 roster reaches 330/330 production-ready;
- Step, Watch, Replay, and Turbo share the resolver/event stream;
- future compatible content normally requires data/compiler work, not resolver code.

## Execution discipline

- Re-read `IRON_PIT_RULES_CONTRACT.md` before combat-mechanic work.
- Verify authoritative RAW before implementing a mechanic variant.
- Inspect current repository APIs before coding; do not invent library/project interfaces.
- At ~130 lines, extract by domain before adding behavior.
- Catch errors at meaningful compiler/export/runtime boundaries; never swallow rules failures or substitute fake defaults.
- Batch related implementation work; do not burn CI on every micro-edit.
- Do not stop at a status message while an identified repository task can still be completed in the current work session.

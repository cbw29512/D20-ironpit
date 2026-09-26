# Canonical Combat Resolution Pipeline

Status: authoritative implementation pattern for new and refactored Iron Pit combat behavior.

This document makes the engine rule explicit:

`combat = checks -> modifiers -> result -> state update -> audit event`

Source ability names describe **why** a rule applies. They are never a separate combat engine.

## 1. Canonical resolution sequence

Every combat-relevant action or effect must flow through the same conceptual sequence:

1. **Declare intent**
   - action/effect id;
   - source combatant;
   - target or area;
   - source ability name for presentation/audit.

2. **Check legality**
   - action economy;
   - resource availability;
   - target validity;
   - range/reach/geometry;
   - movement/path requirements;
   - timing/trigger requirements;
   - ruleset availability.

3. **Collect applicable modifiers**
   - buffs and debuffs;
   - Advantage/Disadvantage sources;
   - resistances, immunities, vulnerabilities;
   - condition/debuff counters;
   - source-creature qualifiers;
   - magical/nonmagical qualifiers;
   - size/terrain/movement qualifiers;
   - reactions and legal overrides.

4. **Resolve the canonical primitive**
   - attack roll;
   - saving throw;
   - ability check;
   - damage;
   - healing;
   - movement;
   - condition/debuff application;
   - resource spend;
   - concentration/lifecycle;
   - other already-defined universal primitive.

5. **Produce the result**
   - legal/illegal;
   - hit/miss/critical;
   - save success/failure;
   - final damage/healing;
   - effect applied/rejected/removed;
   - movement completed/blocked;
   - resource spent/not spent.

6. **Update mutable combat state**
   - HP/Temporary HP;
   - position/movement remaining;
   - resources;
   - conditions/buffs/debuffs;
   - concentration;
   - replacement form;
   - turn/action state.

7. **Emit audit evidence**
   - exact printed source ability name;
   - generic primitive/check used;
   - relevant inputs and modifiers;
   - resulting state change.

## 2. Source abilities are declarative inputs

A feature, spell, monster trait, item, or subclass ability should normally contribute data to one or more shared checks.

Examples:

- Nature's Ward contributes:
  - poison damage immunity to the shared damage-defense check;
  - Poisoned and disease prevention to the shared debuff-counter check;
  - Charmed/Frightened immunity when the source creature type is Fey or Elemental to the shared condition-immunity check.
- Land's Stride contributes:
  - a nonmagical Difficult Terrain counter;
  - saving-throw Advantage against tagged magical plant impediments.
- Purity of Spirit contributes source-typed attack Disadvantage and condition immunities.

None of those features gets a named resolver.

## 3. Required implementation rule

Before adding combat code, ask:

`Which existing check should this source modify?`

If the answer is an existing check, add declarative state/configuration and reuse it.

A new universal primitive is allowed only when no existing check can reproduce RAW. The implementation audit must record the evidence for that conclusion.

Forbidden patterns include:

- `if class == "druid"` inside a shared resolver;
- `if feature_name == "Nature's Ward"`;
- `if monster_name == ...`;
- duplicate attack/save/damage/condition pipelines for one source;
- treating a display name as mechanical state.

## 4. Defensive check order

When an incoming effect is resolved, the target's defenses are evaluated by semantic identity.

### Damage

`incoming typed damage -> immunity -> resistance -> vulnerability -> final damage`

The source name is audit metadata. The damage type is the mechanical key.

### Conditions and debuffs

`incoming condition/debuff -> matching immunity/counter + qualifiers -> applied or rejected`

Qualifiers may include:

- source creature type;
- magical/nonmagical;
- spell/non-spell;
- effect tags;
- movement cost;
- duration/timing.

### d20 tests

`base roll -> collect Advantage/Disadvantage -> cancellation -> reroll/override rules -> modifier -> result`

Every source is tracked separately for audit, but the roll primitive is shared.

## 5. Refactor rule for legacy special cases

When touching an existing subsystem, inspect it for source-specific branches.

If a branch can be represented as data feeding an existing universal check:

1. add/extend the declarative schema;
2. bind the source to that schema;
3. remove the source-specific resolver branch;
4. add Python and browser parity regressions;
5. re-audit other content that can reuse the same binding.

Do not perform unrelated mass rewrites. Refactor by mechanic family so exact-head behavior remains provable.

## 6. Failure behavior

Unsupported outcome-changing semantics fail closed.

A failed legality check, missing capability, malformed modifier, or unsupported result must not be converted into a different legal action or silently ignored.

Ordinary legal outcomes such as immunity, a blocked debuff, a miss, or a failed path are not engine errors; they are explicit results.

## 7. Test contract

Permanent tests should prove both the source binding and the generic resolver.

For each new binding, cover where relevant:

- matching qualifier -> modifier applies;
- nonmatching qualifier -> modifier does not apply;
- stacking/cancellation;
- resource/timing behavior;
- fresh combat-state rebuild;
- Python/browser parity;
- generated serialization.

Tests should assert semantic outcomes, not merely that a source-specific function was called.

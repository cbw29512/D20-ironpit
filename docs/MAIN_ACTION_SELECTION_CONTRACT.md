# Main Action Selection Contract

Status: inert architecture contract. This tranche defines candidate discovery and Arena selection only; it does not move live Action resolution out of `browser-turn.js`.

## Objective

The universal ability-hook dispatcher solves **when** effects may participate. It must not become tactical AI.

The Main Action path therefore separates:

1. **candidate discovery** — which Action families are legal right now;
2. **Arena selection** — which legal family Iron Pit chooses under the existing certified policy;
3. **resolution** — the selected family resolves through its existing rules module.

Hook/registration order is never tactical preference.

## Data schema

### Provider

```text
MainActionProvider
  id: stable non-empty string
  category: canonical Action-family string
  rulesets: non-empty subset of ["2014", "2024"]
  discover(ctx): null | { payload?: object }
  resolve(ctx, candidate): { events: BattleEvent[], sequence: integer }
```

Providers are static module metadata only. They must not store combat state.

`discover(ctx)` is an eligibility/choice query and must not spend actions, resources, movement, or mutate combat state. It may perform the existing **within-family** choice, such as best spell, best area placement, or best standard attack.

The ephemeral candidate returned to the selector is:

```text
MainActionCandidate
  providerId: string
  category: canonical category
  opportunityProfile: profile that discovered this candidate
  combatantId: combatant that discovered this candidate
  turnKey: turn identity when supplied by the caller
  payload: object
```

### Opportunity profile

An opportunity profile is an ordered list of **allowed categories**. The order is Arena policy, not provider priority.

Canonical profiles for the first migration are:

| Profile | Allowed category order |
|---|---|
| `normalPreMove` | `spell-offense` |
| `normalPostMove` | `spell-offense`, `intimidating-presence-2014`, `attack-action`, `area-save`, `save-action`, `standard-attack`, `dodge` |
| `actionSurgeAttack` | `attack-action`, `standard-attack` |

The Action Surge profile deliberately preserves the currently certified Iron Pit attack-only extra-Action path. Architecture migration must not broaden it into Magic or other Action families.

## Selection invariants

- Candidate discovery and tactical selection are separate APIs.
- Provider registration order is never used as tactical preference.
- The selector walks the selected profile's category order.
- At most one candidate may exist in a category for one opportunity. More than one is a fail-closed architecture error; split the category or define explicit policy instead of relying on insertion order.
- Candidates outside the selected opportunity profile are ignored and need not be discovered.
- A candidate is bound to the opportunity profile that discovered it; resolution rejects cross-profile reuse.
- A candidate is also bound to its discovering combatant and turn key; resolution rejects stale or cross-actor reuse.
- Ruleset scope is explicit on every provider.
- Candidate discovery is side-effect free.
- Resolution remains owned by the existing Action-family module.
- The normal pre-move and post-move opportunities recompute candidates because movement can change legality.
- Charge/closing and offensive movement remain outside Main Action candidate selection.
- Support actions, Bonus Actions, reactions, and end-turn cleanup remain outside this contract.

## Certified policy to preserve

Python and browser currently use the same normal-turn preference:

1. pre-move best spell offense;
2. charge/closing and offensive movement;
3. post-move best spell offense;
4. 2014 Intimidating Presence;
5. Attack/Multiattack action;
6. area save action;
7. single-target save action;
8. standard attack;
9. Dodge fallback.

The migration changes orchestration, not those choices.

## Current migration status

The provider-discovery tranche is intentionally **inert**. Live `browser-turn.js` still owns Main Action ordering.

Registered discovery providers now cover:

- spell offense;
- 2014 Intimidating Presence;
- Attack/Multiattack action;
- area save action;
- single-target save action;
- standard attack;
- Dodge.

Provider discovery delegates to existing family policy rather than duplicating rules. The spell offense module exposes its existing attack-vs-save choice as a side-effect-free `choose()`, Attack/Multiattack exposes side-effect-free availability, and single-target save choice lives in a shared save-action policy used by the current live turn and future provider.

Certified offensive hero spell attacks/save spells are currently all Action-timed. A permanent artifact regression fails if a future certified offensive spell becomes Bonus Action-timed without an explicit architecture change.

The provider layer does not route live turns yet and therefore must not alter combat outcomes or certification counts.

## Migration plan

1. Land this candidate registry/selector inert with adversarial tests and production wiring.
2. Register providers without routing live turn behavior through them; prove discovery parity.
3. Route `normalPreMove` through the selector.
4. Route `normalPostMove` through the selector and remove named Action-family branches from `browser-turn.js`.
5. Reuse the same selector infrastructure for Action Surge with the restrictive `actionSurgeAttack` profile.
6. Keep Python as the rules oracle and add permanent Python/browser policy-parity tests before each live behavior migration.

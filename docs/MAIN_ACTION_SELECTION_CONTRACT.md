# Main Action Selection Contract

Status: Action Surge live-migration tranche. Both normal-turn Main Action opportunities and the restrictive attack-only Action Surge opportunity route through the selector.

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

## Registered provider families

The browser registers providers for all seven normal-turn Action families: spell offense, 2014 Intimidating Presence, Attack/Multiattack, area save, save action, standard attack, and Dodge. Provider discovery reuses the existing pure choice/legality paths; both normal-turn opportunities now resolve through the selector.

`browser-spell-offense.js` exposes a pure `choose()` plus `resolveChoice()` split so discovery can select the same attack-vs-save spell without casting it. `browser-multiattack.js` exposes normal-turn `available()` plus pure `hasLegalChoice()` so Action Surge can prove Attack Action legality while the normal Action is already spent.

The existing single-target save fallback is preserved exactly, including its historical behavior after the dedicated area-save opportunity. Policy cleanup is deliberately out of scope for this architecture migration.

## Live migration status

`normalPreMove` is the first live selector route. Its profile allows only `spell-offense`, so this migration changes orchestration without introducing category competition. If a legal pre-move spell candidate exists, the selector resolves it through the existing spell-offense provider; if none exists, sequence and state pass through unchanged to the existing charge/movement path.

`normalPostMove` now recomputes the full legal candidate set after charge/offensive movement, selects by the certified Arena category order, and resolves exactly one Action family. The named spell/presence/Attack Action/area-save/save/standard-attack/Dodge branches have been removed from `browser-turn.js`.

`actionSurgeAttack` discovers only Attack Action and standard-attack candidates while the normal Action is already spent. Discovery does not grant the extra Action or spend the resource. If no legal attack candidate exists, Action Surge remains unused; after a candidate is selected, Action Surge grants the extra Action and the same candidate resolves through the shared provider path.

## Migration plan

1. Land this candidate registry/selector inert with adversarial tests and production wiring.
2. Register providers without routing live turn behavior through them; prove discovery parity.
3. Route `normalPreMove` through the selector.
4. Route `normalPostMove` through the selector and remove named Action-family branches from `browser-turn.js`. **Complete.**
5. Reuse the same selector infrastructure for Action Surge with the restrictive `actionSurgeAttack` profile. **Complete.**
6. Keep Python as the rules oracle and add permanent Python/browser policy-parity tests before each live behavior migration.

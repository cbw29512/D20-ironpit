# Start-turn condition aura tranche

## Ownership and objective

- Agent: ChatGPT; status: ACTIVE.
- Branch: `fix/shared-start-turn-condition-auras`.
- Coordination issue: #538; starting main: `40de77f60f317f413395e4872c443b58af77d2b9`.
- Subsystem: passive start-turn condition aura binding and existing aura parity.
- Expected files: timed-aura schema, existing emanation discovery/condition resolver,
  source binding/audit, focused Python/browser tests, CI regression registration,
  generator-owned combat data and certification artifacts.
- #585 is stale/conflicted at `3a5bafd15a91cd0e8b52661b7abeee01014ab0ea`.
  Its schema/serializer/post-hit/cleric surfaces are excluded. The only intended
  common file is CI, where this tranche adds one independent regression command.
- Grok's images, portraits, figure profiles and visual presentation remain excluded.
- No Netlify publish. No lair actions.

## Source and semantic decomposition

Pinned SRD 5.1 and SRD 5.2.1 source records are authoritative for these bindings.
Official comparison: D&D Beyond Hezrou records 16922 and 5195073.

| Source | Radius | Constitution DC | Failure | Success |
|---|---:|---:|---|---|
| 2014 Ghast | 5 ft | 10 | Poisoned until target's next turn starts | Match immunity to this source |
| 2014 Hezrou | 10 ft | 14 | Same | Match immunity to this source |
| 2024 Ghast | 5 ft | 10 | Same | Match immunity to this source |
| 2024 Hezrou | 10 ft | 16 | Same | No source immunity |

Classification: ENGINE_EXISTS_BINDING_MISSING + ENGINE_EXISTS_PARAMETER_DELTA.
No Action, Bonus Action, Reaction, resource, recharge, or activation is required.
The Pit's existing offensive ally-safe area policy remains authoritative (§10).

## State-first reuse/parity map

- Immutable: existing `TimedSelfBuffAction` plus `TimedHostileConditionAura`.
  Passive activation selects existing aura discovery without creating a timer
  on the source. Condition duration/expiry are declared on the aura payload.
- Mutable: ordinary source-owned `poisoned` timed effects and existing
  `source_effect_immunity` marks on the target; nothing mutates the source card.
- Python: `timed_emanations` discovery -> `hostile_condition_auras` -> shared
  `condition_is_immune`, `resolve_saving_throw`, `apply_timed_condition`,
  `grant_source_effect_immunity` and target-turn condition lifecycle.
- Browser: existing `browser-timed-emanations` turn-start hook -> the same
  condition-immunity/save/timed-condition/immunity runtimes.
- Serialization: existing timed-self-buff serializer already emits activation
  and the complete aura payload. No new combatant-schema field is needed.
- Reset: fresh fight state has no Poisoned or source-immunity marks. No new pool.
- Tests: source values; first-turn passive discovery; range/footprints; dead
  source; immunity skips dice; poison damage immunity is independent; contextual
  save modifiers; target-start expiry; separate sources; source-specific immunity;
  fresh-state/card immutability; 2024 success does not invent immunity.

## Current verification and remaining debt

Starting generated counts: 2014 175/327; 2024 141/330; heroes 240/240 each.
Current-main report independently compiles all 175 2014 candidates.
Ghast still has Turning Defiance; binding Stench alone must not certify it.
Hezrou is the immediate 2014 trait-only unlock.
Implementation and the touched-subsystem debt audit are complete. Current local
generated counts are 2014 176/327 and 2024 141/330; heroes remain 240/240 each.
The full Python suite passed (2,632 tests), all 213 browser CI regression commands
passed, and final focused source/lifecycle tests passed (22 tests). Exporters,
manifest parity, capability checks and source limits passed. Exact PR-head GitHub
Actions certification remains pending; local results do not substitute for it.

Resolved parity debt: both aura runtimes now supply complete saving-throw context,
honor condition immunity before dice, and use the existing target-turn-start
lifecycle (including another turn in the same round). Passive source discovery
uses the existing aura mechanism without source timers, resources or activation.
No open A-class correctness or B-class architecture debt remains in this tranche.

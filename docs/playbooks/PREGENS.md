# Pregen implementation — source-legal builds

Use the [common execution manual](../IRON_PIT_IMPLEMENTATION_PLAYBOOK.md) and [SOUL](../../SOUL.md). This lane applies to classes, subclasses, feats, spells, items, level progression and canonical player-character builds; it never creates an alternate combat engine.

## Card parameters vs runtime

Immutable pregen data owns edition, class/subclass, level, legal choices, abilities, AC/HP, weapon/spell profiles, resources, printed names, DCs, dice, ranges and durations. The **same engine as monsters** owns attacks, saves, conditions, typed damage/healing, Action/Bonus Action/Reaction, movement, concentration, and fight-local state/reset. Every ability must pass the source-neutral [card-to-combat contract](../UNIVERSAL_CARD_COMBAT_CONTRACT.md).

## Implementation

1. Read the exact 2014 or 2024 source and [canonical build policy](../CANONICAL_COMBAT_BUILD_POLICY.md). Do not claim a legal build from memory, copied edition numbers or a higher-level card omitting mandatory features.
2. Decompose each combat feature as `trigger → eligibility/action/resources → roll/save → typed effects → duration/exit/reset`; read the [generated inventory](../UNIVERSAL_MECHANIC_INVENTORY.md) and search **monster and pregen** resolvers.
3. Reuse, parameterize, or compose existing universal primitives. Only a genuinely missing semantic creates deliberate engine work after the current content pass; park its dependent level/card fail-closed in the meantime.
4. Bind exact source/build choices in immutable template data. Advance legal levels in order, with source-specific 2014/2024 differences kept independent.
5. Verify representative Python and browser behavior, source reset, serializer output, generated snapshots/manifest and exact-final-head CI. Re-audit monsters for newly reusable primitives.

Example: Lay on Hands is generic action economy + resource spend + HP healing/allowed condition removal + targeting, with edition values on the source card; not a Paladin-specific healing resolver.

**Done:** source legal, all mandatory combat behavior present, immutable cards and fresh fight state, exact-edition data, permanent parity evidence, updated generator outputs and the required final-head certification gates.

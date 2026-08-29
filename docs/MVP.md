# Iron Pit — Locked Product Acceptance Target

## Definition of Done

The current product milestone is complete when a user can open the deployed static site, choose 1–8 RAW-ready hero cards and 1–8 RAW-ready monster cards, press **FIGHT**, and watch the browser replay a rules-resolved stick-figure deathmatch until one side is actually dead.

The standard Pit starts combatants 30 feet apart. A 5-foot option exists for already-engaged testing. Long-distance ranged-duel modes are not part of the standard product.

## Required combat behavior

- Browser-secure random dice.
- Initiative and initiative modifiers.
- Attack rolls against Armor Class.
- Natural 1 misses and natural 20 critical hits.
- Critical weapon damage dice.
- Typed damage, HP, temporary HP, Resistance, Immunity, and Vulnerability where certified.
- Advantage/disadvantage with both d20 results preserved.
- Legal melee/ranged range handling and ranged-in-melee Disadvantage.
- Multiattack/Extra Attack action economy and legal retargeting.
- Combatants use legal ranged/thrown offense while closing, then spend remaining movement toward the melee brawl.
- No kiting, retreat, surrender, morale, or range-preserving movement.
- Once engaged, legal melee attacks are preferred.
- Standard monsters die at 0 HP.
- Player characters use supported Unconscious, Death Saving Throw, damage-at-0, massive-damage, and recovery rules.
- A living player character at 0 HP does not end the match.
- When no standing enemy remains, downed living player characters remain targetable so the deathmatch can reach a rules-resolved death.
- Attacks against Unconscious targets apply the supported Advantage and close-range critical-hit rules.
- Unsupported outcome-changing mechanics fail closed.

## Required presentation behavior

- The selected card teams remain visible.
- Pressing **FIGHT** reveals the live Pit.
- Each selected combatant has a stick-figure representation and HP bar.
- Initiative, movement, attacks, hits, healing, death saves, critical hits, unconscious states, and deaths replay from the same authoritative browser event stream used for the result.
- The result panel appears after the replay and distinguishes Alive, Unconscious/Stable, and Dead states.
- The detailed battle log remains available for rules auditing.
- Reduced-motion preferences are respected.

## Required platform behavior

- GitHub is the source of truth.
- Netlify serves the production static site.
- Production combat has no backend/API dependency.
- Python remains the CI/reference rules oracle.
- Non-production Netlify builds remain skipped to protect deploy credits.
- Exact-head CI must pass before a content count or mechanic is called certified.

## Content acceptance

- The full SRD 5.2.1 monster catalog remains 330 unique records with source metadata.
- Only explicitly audited monster templates are runnable.
- The hero catalog may contain planned builds, but only explicitly audited builds are runnable.
- New content never bypasses missing outcome-changing mechanics.

## Next mechanics after the core Pit is certified

Saving throws, Grappled, Restrained, broader conditions and riders, reactions, recharge actions, and spellcasting are added as reusable engine capabilities. Monster and hero coverage expands behind those capabilities instead of approximating unsupported rules.

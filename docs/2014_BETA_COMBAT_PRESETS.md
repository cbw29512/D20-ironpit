# Purpose-built 2014 beta fights

Chris requested one-click prearranged fights, including a Barbarian against two
Goblins and parties up to six heroes against six monsters, with the explicit
purpose of testing varied combat rules and abilities.

The immutable recipes in `frontend/combat-presets.js` select certified 2014
class/level snapshots and certified monster template IDs. They contain no rolls,
combat state, positioning overrides, AI overrides or rules resolvers. The loader
validates the complete recipe before replacing the six slots on each side,
clears the prior result/session/Turbo state using the existing lifecycle, and
leaves execution to Fight, Step, Watch, Turbo and Replay. Loading is blocked
during active combat. Source cards remain immutable during engine execution.

Twelve fights cover every class and the requested party sizes. The seven size
progression fights cover ki, Rage, Extra Attack, healing, concentration, spell
selection against immunity, auras, ranged attacks, area geometry, reactions and
team/resource pressure. Additional fights isolate grappling, poison, undead
defenses and level 20 martial/caster abilities. The two level 20 fights are
ability checks rather than claims of equivalent hero and monster power.

“Look for” text describes opportunities, not promised event coverage. Dice and
the existing Arena AI may not trigger every listed feature in one run. This
suite does not establish exhaustive RAW correctness or cover unavailable
monster mechanics. Step and expandable Battle Log audits support inspection;
Turbo and replay support repeated outcomes without rigging rolls.

Difficulty labels use the 2014 XP thresholds and monster-count multipliers,
including the party-size adjustments for fewer than three or at least six
heroes. The presets use comparable-CR monsters within each fight. CR is not
equated to character level, and the labels do not promise equal win rates.
Source: [2014 Basic Rules, Building Combat Encounters](https://www.dndbeyond.com/sources/dnd/basic-rules-2014/building-combat-encounters).

Permanent tests validate all recipes against the actual catalog, every class
and requested size, immutability, party-size XP examples, canonical seeded
engine completion, one-click loading and protection against active-session
replacement. No new combat primitive or Python/browser parity hook is needed:
the sole change is selection and presentation around the existing engine.

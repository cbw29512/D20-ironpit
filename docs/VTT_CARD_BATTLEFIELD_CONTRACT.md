# Iron Pit VTT Card Battlefield Contract

This document records the approved battlefield direction for D20 Iron Pit. It is a specific battlefield/UI architecture contract and supersedes older fixed-formation/deity-closing assumptions wherever they conflict.

## Product decision

Iron Pit uses one persistent tactical battle map. Combatants are represented by the user's Iron Pit/DNDCards artwork as moving battlefield cards/tokens rather than by separate generic circles or by static combat cards outside the map.

The battlefield card is a visual projection of the immutable combatant template plus mutable fight state. The visual never owns rules.

## Authoritative battlefield state

- The combat engine owns one authoritative square grid.
- Each grid cell represents 5 feet.
- Every combatant has an actual grid position during combat.
- Voluntary movement consumes the creature's actual effective movement speed under the selected ruleset.
- Movement, reach, range, Opportunity Attacks, forced movement, line of sight, collision, areas of effect, auras, and positioning-sensitive Advantage/Disadvantage all consume the same position state.
- The old scalar-distance/fixed-formation model is migration scaffolding only and must be removed after all canonical combat paths consume grid state.

## Creature footprint

Printed creature size determines occupied grid footprint; monster names never do.

- Tiny, Small, Medium: 1 x 1 grid cell for the 5-foot VTT representation.
- Large: 2 x 2 cells.
- Huge: 3 x 3 cells.
- Gargantuan: 4 x 4 cells unless a more specific source rule requires a larger space.

Footprint is derived from immutable size data. Runtime state stores position, not a duplicated monster-specific size override unless a supported transformation changes size.

## Movement

- Use the selected ruleset's Playing on a Grid rules.
- A 5-foot adjacent orthogonal or diagonal square costs 5 feet of movement unless a specific rule changes the cost.
- A combatant cannot end normal movement in an occupied illegal space.
- Large footprints must fit completely inside legal map bounds and cannot overlap another occupying creature unless a specific rule permits it.
- Dash, Disengage, difficult terrain, Grappled, Prone, speed changes, teleports, forced movement, flight, swim, burrow, and other movement rules feed the same movement/position engine.
- Iron Pit no longer grants free ordinary closing. Arena design and AI policy prevent degenerate fleeing/kiting rather than bypassing printed movement.

## Areas and targeting

Area shape is an engine primitive; the source supplies shape and dimensions.

Examples of declarative inputs:

- line: length + width;
- cone: length;
- sphere/radius: radius;
- emanation: radius from source;
- cylinder: radius + height when height matters.

The geometry engine determines which occupied cells and creature footprints intersect the area. Each affected creature resolves its own required saving throw/effect unless the source explicitly says otherwise.

A dragon's Lightning Breath is not coded as "hit two targets." It is a line with source-defined dimensions. If two combatants are physically aligned inside that line, both are affected; if one is outside the line, it is not.

## Card-as-token presentation

The moving battlefield representation uses the user's card art and identity.

- Card/token dimensions visually scale to the creature footprint while preserving readable artwork.
- The token displays compact live combat data such as current HP and Temporary HP.
- Buff/debuff/condition/resource symbols render as overlays around/on the card.
- Overlay state is read-only presentation derived from engine state; icons never create, remove, or alter a rule effect.
- Selecting/clicking the battlefield card opens the full card/stat presentation.
- The immutable original card remains the source identity; mutable overlays reset with combat state after the fight.

## Live overlay categories

The overlay system must be data-driven and reusable. It should support at least:

- conditions;
- buffs and debuffs;
- concentration;
- Temporary HP;
- recharge ready/expended state;
- limited resources when useful to the viewer;
- Reaction availability when useful to the viewer;
- major combat-state flags such as unconscious, stable, dead, restrained, or prone.

The visual registry maps an engine state/effect id to an icon/style. It never checks a monster name.

## Execution-mode invariant

Step, Watch, Replay, and Turbo continue to use the exact same combat resolver and grid state. Watch/Step may animate card movement; Replay reuses recorded deterministic positions/events; Turbo may suppress rendering but must not simplify movement or geometry.

## BattleCast research reference

BattleCast was reviewed as a reference implementation before this contract was written. Useful patterns confirmed in its public engine include:

- pure geometry separated from state mutation;
- real x/y grid positions;
- footprint-aware collision and range;
- 5-foot cells with diagonal adjacency;
- Large/Huge/Gargantuan multi-cell footprints;
- one movement authority with path validation;
- cone, line, and sphere geometry;
- seeded/replayable battle state in the extracted engine.

Reference sources:

- https://battlecast.gg/
- https://github.com/bjedrzejewski/battlecast-engine
- https://github.com/bjedrzejewski/battlecast-engine/blob/main/DESIGN.md
- https://github.com/bjedrzejewski/battlecast-engine/blob/main/src/engine/combat-geometry.ts

BattleCast's extracted engine is MIT licensed. This Iron Pit tranche uses the architecture as research/reference; any future direct copied/substantial code must preserve the applicable MIT copyright/license notice and provenance.

## Migration order

1. Lock this contract and update repository agent guidance.
2. Add universal grid/map/position schemas and Python/browser geometry parity.
3. Replace scalar distance with footprint-aware range/reach queries.
4. Replace free closing with real movement/path legality.
5. Route Opportunity Attacks and forced movement through grid movement.
6. Add line/cone/radius/emanation targeting against occupied footprints.
7. Bind Recharge breath weapons and other area actions to the shared geometry/save engines.
8. Replace the current battlefield presentation with the moving card-token VTT and live overlays.
9. Remove migration-only fixed-formation/scalar-distance code after no certified path depends on it.
10. Re-audit all 330 monsters and canonical heroes after each universal capability tranche.

# Purpose-built website test fights

Chris requested one-click prearranged fights whose listed mechanics actually
happen. The immutable recipes in `frontend/combat-preset-recipes.js` select
certified class/level snapshots and certified monster template IDs for 2014
and 2024. They contain no rolls, combat state, positioning overrides, AI
overrides or rules resolvers. The loader validates the complete recipe,
switches the ruleset when a 2024 fight is chosen, replaces the six slots on
each side, and leaves live execution to Fight, Step, Watch, Turbo and Replay.

**Load Combat** is review-only. After a purpose-built fight is selected from
the list, it replays that recipe's recorded seed through the existing replay
resolver and presents the complete event log in a dedicated dialog. It does
not add a combat mode, change dice, or alter asserted preset mechanics.

Each recipe records a probe seed and one or more required aspects. The
browser test runs that seed and fails if any named aspect is missing from
the event stream, if the fight throws, or if a pit-banned option
(teleport, plane shift, summoning, vertical flight) appears. “Look for”
text on the website matches those asserted aspects, not optional color. If
dice can skip a feature, the seed or roster must change until the aspect
resolves under the landing-damage Action policy.

Thirteen 2014 fights and twelve 2024 fights cover every class and party sizes
1v1 through 6v6: melee, spells, healing, conditions, undead defenses,
legendary actions, and high-level resources. 2024 recipes use certified 2024
pregen snapshots and certified `srd-` monster templates only. The 2014
`legendary` recipe is Karnok versus the certified 2014 Unicorn and asserts
that a printed legendary action actually fires. Teleport and Dispel Evil and
Good Dismissal stay omitted under the pit bans; the remaining printed Unicorn
block is bound.

Difficulty labels use the 2014 XP thresholds and monster-count multipliers
as a rough estimate. They do not promise equal win rates.

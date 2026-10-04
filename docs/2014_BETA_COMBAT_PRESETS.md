# Purpose-built website test fights

Chris requested one-click prearranged fights whose listed mechanics actually
happen. The immutable recipes in `frontend/combat-preset-recipes.js` select
certified class/level snapshots and certified monster template IDs for 2014
and 2024. They contain no rolls, combat state, positioning overrides, AI
overrides or rules resolvers. The loader validates the complete recipe,
switches the ruleset when a 2024 fight is chosen, replaces the six slots on
each side, and leaves execution to Fight, Step, Watch, Turbo and Replay.

Each recipe records a probe seed and one or more required aspects. The
browser test runs that seed and fails if any named aspect is missing from
the event stream, if the fight throws, or if a pit-banned option
(teleport, plane shift, summoning, vertical flight) appears. “Look for”
text on the website matches those asserted aspects, not optional color. If
dice can skip a feature, the seed or roster must change until the aspect
resolves under the landing-damage Action policy.

Twelve 2014 fights and twelve 2024 fights cover every class and party sizes
1v1 through 6v6: melee, spells, healing, conditions, undead defenses, and
high-level resources. 2024 recipes use certified 2024 pregen snapshots and
certified `srd-` monster templates only. Legendary actions are included only
when a certified monster actually has them; the current certified 2014 and
2024 website rosters do not expose legendary-action monsters, so those fights
use undead and breath/recharge monsters instead.

Difficulty labels use the 2014 XP thresholds and monster-count multipliers
as a rough estimate. They do not promise equal win rates.

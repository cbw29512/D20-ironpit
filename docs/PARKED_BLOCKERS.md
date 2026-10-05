# Parked blockers

Working list of 2014 roster blockers set aside so a lane can keep moving. The Chris-locked rules **index** is `docs/IRON_PIT_LOCKED_RULES.md` (PR #602). This file does not replace that index or `docs/IRON_PIT_RULES_CONTRACT.md`.

When #602 lands a Parked blockers section, fold this table there and delete this file.

| Family | Creatures | Why parked | Next primitive |
|---|---|---|---|
| Sleep Breath | Brass wyrmling / young / adult / ancient | Failed-save Unconscious plus `allowed_removal_action_ids: wake-sleeper`; no wake-sleeper action exists | Extend FailedSaveTimedEffect removal + a generic wake-sleeper Action |
| Slowing Breath / Slow | Copper dragons; Stone Golem | `slowed` is not a universal condition (speed, reactions, action/bonus exclusive, max attacks) | New parameterized slow rider, not a new condition name |
| Weakening Breath | Gold dragons | `weakened-strength` Strength-check/attack Disadvantage is not a universal condition | Existing Disadvantage grant if it can be timed/repeat-saved |
| Petrifying Breath | Gorgon | `repeat_save_failure_condition_id: petrified` escalation | Same petrify machine as Cockatrice; do not invent here |
| Change Shape | Adult / ancient metallic dragons | Extra Action that replaces the combatant form | Park until polymorph/form-replace policy is opened |
| Horror Nimbus | Nalfeshnee | Recharge + Frightened already compile; leftover `mechanic:defense` | Defense-text family, not this lane |
| Blinding Spittle | Gibbering Mouther | Recharge + Blinded already compile; leftover multiattack / extra-action / trait | Separate multiattack-complex lane |
| Swallow | Giant Frog, Giant Toad, Purple Worm, Remorhaz, Behir, Kraken, Tarrasque | Swallowed state (blinded + restrained + total cover + start-turn acid + death/regurgitate exit) is a new machine | Do not fake swallow as Grappled |
| Attach / Blood Drain | Stirge | Ongoing attach, source-attack lock, detach movement, HP-loss end | New attach rider, not a Grapple rename |
| Reel / pull | Roper | Tendril attach + pull toward source | Forced-movement pull primitive; only push exists |
| Engulf | Gelatinous Cube, Shambling Mound | Cube/mound engulf is swallow-shaped plus form-specific extras | Same swallow machine, then extras |

# Grick conditional sequence audit

Owner ChatGPT; branch `feat/2014-grick-followup`. Active source and shared sequence tranche. Exact starting main `ec84f726f799f03db78beacfe433c85b353f270f`. Preceding family #632 cleared both Veterans; accepted roster 189/327.

Source wording: one Tentacles attack, then one Beak attack only if the first hits, against that same target. Semantics missing from ordinary sequence slots: immediate previous-slot hit requirement and actual target identity. Ordinary attacks, costs, dice, hit/damage, targets/barriers/range, reactions, death/interruption and reset already exist. `ENGINE_TRULY_MISSING` applies only to the two narrow sequence constraints. No source-name runtime dispatch or second attack resolver.

Immutable `PreviousAttackRequirement` is optional on a shared `AttackActionSlot`. Empty/malformed conditions and predicates on a first/save-adjacent slot fail before mutation. Source proof requires exact policy, wording, two single-attack slots, names/kinds and every attack ID. Python/browser both keep only the preceding slot's actual attack event within the Action, evaluate conditions, then reuse normal attack choice with an optional target ID. Current legality is checked after all earlier damage/reactions; dead/out-of-range targets cannot be replaced. Redirected attacks record the actual affected creature. Natural 1/turn termination remain ordinary engine behavior. No new fight state, timers or resources.

Preview assumes a legal preceding attack hits to preserve the existing printed maximum mean-damage selection policy (Tentacles 9 + Beak 5.5 = 14.5). Preview conditions share the target guard and never make a follow-up independently legal when its prerequisite cannot attack. This is potential printed damage, not probability-weighted DPR.

Permanent source/compiler/serializer/browser fixture has eight scenarios: hit, miss, natural 1, target death, target-order change, movement out of range, redirected first hit, and a synthetic follow-up-only-in-range profile. Mutation tests cover source wording/count/policy/IDs/names and schema guards; cards remain immutable and fresh state clears costs/termination. Focused verification only; final-head CI pending.

Native 2024 audit: Grick makes one Beak and one Tentacles attack without a previous-hit condition. Beak is 2d6+2 Piercing; Tentacles is 1d10+2 Slashing and has an independently declared Medium-or-smaller grapple rider (escape DC 12). Printed order and numbers differ from 2014. No 2014 predicate/dice/order are copied; normal slots remain unchanged. 2024 readiness stays 141/330.

Focused verification: 58 Python source/schema/sequence cases passed, eight new browser parity scenarios passed, and the existing complete-sequence and Veteran browser fixtures passed through the changed selector. One final-head CI pass follows completed generation/re-anchor.

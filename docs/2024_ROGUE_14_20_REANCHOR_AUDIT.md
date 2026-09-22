# 2024 Rogue 14–20 re-anchor audit

Baseline: `main` at `a7a775eac1882f5a3f38a994ae0fce8eeafdc61e`.

Authoritative rules source: D&D Beyond Basic Rules 2024 / SRD 5.2.1 Rogue and Thief. This audit is intentionally capability-first: feature names do not justify new engine code when an equivalent universal primitive already exists.

| Level | RAW delta | Engine disposition on current architecture | Re-anchor action |
|---|---|---|---|
| 14 | Devious Strikes; Sneak Attack remains 7d6 | Cunning Strike die-cost/save/condition path already exists. Obscure is a save-to-Blinded rider and should reuse timed conditions. Daze/Knock Out must remain fail-closed unless their complete action/lifecycle semantics are certified. | Port only data/capability extensions and parity regressions; no Rogue-name dispatch. |
| 15 | Slippery Mind; Sneak Attack 8d6 | Generic source-tagged saving-throw proficiency grants are the correct primitive. | Reuse save-proficiency grant for Wisdom + Charisma; verify derived save bonuses in Python/browser. |
| 16 | Ability Score Improvement; Sneak Attack remains 8d6 | Pure progression/stat derivation. | Apply the canonical audited ASI only; no resolver change. |
| 17 | Thief's Reflexes; PB +6; Sneak Attack 9d6 | Generic first-round extra-turn scheduling is the correct primitive. The extra turn is Initiative -10 and must run the ordinary turn lifecycle. | Reuse scheduler; source-tag the grant; prove round 2+ order is unchanged. |
| 18 | Elusive; Sneak Attack remains 9d6 | Generic defender-side attack-Advantage suppression unless Incapacitated. | Reuse suppression primitive; preserve Disadvantage and normal cancellation semantics. |
| 19 | Epic Boon; Sneak Attack 10d6 | Boon choice is build data. If Boon of Combat Prowess is retained by the canonical build, its Peerless Aim effect maps to generic once-per-turn miss-to-hit. | Reuse miss-to-hit primitive and verify ordering after final hit determination but before miss-only hooks. |
| 20 | Stroke of Luck; Sneak Attack remains 10d6 | Generic finite D20-result override is required for failed D20 Tests. Attack use must not duplicate Peerless Aim and must preserve raw dice in audit history. | Reuse/port generic selected-result override; verify attack/save paths, resource spend, Short/Long Rest recovery, and browser parity. |

## RAW checkpoints

- Rogue progression: L14 Devious Strikes, L15 Slippery Mind, L16 ASI, L17 subclass feature, L18 Elusive, L19 Epic Boon, L20 Stroke of Luck; Sneak Attack scales 7d6, 8d6, 8d6, 9d6, 9d6, 10d6, 10d6 respectively.
- Devious Strikes options are Daze (2d6, CON save), Knock Out (6d6, CON save), and Obscure (3d6, DEX save; Blinded until end of target's next turn).
- Slippery Mind grants Wisdom and Charisma saving-throw proficiency.
- Thief's Reflexes grants two turns in round 1, at normal Initiative and Initiative minus 10.
- Elusive prevents attack-roll Advantage against the Rogue unless Incapacitated.
- Stroke of Luck turns a failed D20 Test roll into 20 and recharges on a Short or Long Rest.

## Certification gate

No level in this tranche is READY merely because this audit exists. Each snapshot must be produced from the canonical progression, pass Python certification, pass browser parity, regenerate static artifacts, and leave the generated manifest current. Missing semantics remain blockers rather than approximations.

## Integration note

The older stacked 2024 Rogue 14–20 branches predate the current main and are materially divergent. Do not merge them wholesale. Re-anchor level-by-level from current main, transplanting only the smallest audited capability/data delta and its permanent tests. The same rule applies to the 2014 Rogue 17–20 branch: its primitives are reusable, but the branch must be reconciled with current main before merge rather than overwriting concurrent engine work.

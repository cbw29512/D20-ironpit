# Monster Implementation Guide

Read `SOUL.md`, this file, and `docs/CURRENT_OPERATING_STATUS.md` before monster work.

## Loop

1. Read the exact source card and edition.
2. Ignore the ability name. Write:
   `trigger/timing -> cost/resource -> attack/check/save -> effect -> duration -> exits/reset`.
3. Search existing monster **and pregen** mechanics for each semantic piece.
4. Reuse/compose universal primitives. Source-specific numbers stay data.
5. Prove the smallest representative monster first.
6. Apply the same binding to every mechanically identical family member.
7. Run one focused family check; regenerate outputs; let one final-head CI pass do the broad verification.
8. Update tracker/blocker truth and take the next real blocker.

Never add monster-name dispatch or a named-ability resolver when generic mechanics already cover the behavior.

## Example — 2014 Brass Dragon Sleep Breath

Behavior:
`Action -> shared breath Recharge 5–6 -> cone -> CON save -> failed save Unconscious ->
ends on damage OR ally Action to wake -> otherwise duration expires`.

Reuse:
- `SavingThrowAction` + cone targeting
- shared breath resource/recharge
- universal `unconscious`
- failed-save timed effect
- `ends_on_damage`
- generic Action-based condition removal: `wake-sleeper`

Do **not** create a Sleep Breath or Brass Dragon resolver.

Sample order:
1. Wyrmling: DC 11, 15-ft cone, 1 minute.
2. Young: same mechanics, its own DC/range/duration.
3. Adult: same mechanics, its own DC/range/duration.
4. Ancient: reuse Sleep mechanics; keep unrelated blockers separate.

Printed name remains **Sleep Breath** in logs. Parameters never copy across ages/editions without source evidence.

## Done means

Source exact, immutable card data, temporary fight state, Python/browser parity, no duplicate engine,
family rebound, generated artifacts refreshed, blocker truth updated, focused check + exact-head CI green.

Open the long rules/architecture files only when this guide is insufficient, a subsystem changes,
or source/semantic interpretation is uncertain.

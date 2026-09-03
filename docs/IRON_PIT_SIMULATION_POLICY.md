# Iron Pit Simulation Policy

Iron Pit is a D&D 5e (2024) / SRD 5.2.1-compatible combat simulator, not an exact tabletop emulator. Source data stays faithful to the SRD; the arena engine intentionally normalizes rules that would otherwise require battlefield geometry, repeated DM rulings, or monster-specific AI.

## Engine-first rule

1. Implement a shared combat mechanic once.
2. Keep monster and pregen definitions declarative: statistics, attacks, spells, defenses, and printed riders.
3. Certify compatible creatures/builds in batches.
4. Treat non-combat rules as arena-neutral.
5. Add a true exception only when no reusable mechanic can represent a combat-relevant rule.

## Arena decision order

### Before combat

- A combatant may commit at most one supported opening buff.
- The same buff is never stacked with itself.
- Movement/ambush openers are available only in round 1 when that creature or shared initiative group strictly beats every enemy initiative total. A tie does not qualify.

### On a turn

1. Resolve urgent survival/support behavior.
2. If Bloodied (at or below half effective maximum HP) and a legal heal is available, prefer healing before ordinary offense.
3. If separated and a usable true-range attack or spell is available, use ranged offense.
4. Once an enemy is within melee range, prefer a legal melee option.
5. Without usable true-range offense, close toward melee and fight.

Iron Pit does not use routine kiting. Ordinary Disengage, Dash-for-positioning, and similar geometry-only choices are arena-neutral unless a printed feature adds a direct combat consequence.

## Openers

Charge, Pounce, Running Leap, rushes, movement-triggered strikes, and compatible ambush effects use the same opener gate:

- round 1 only;
- strict initiative sweep over every enemy;
- then resolve the source-backed attack/rider;
- afterward combat proceeds normally.

## Poisoned

Iron Pit uses one Poisoned lifecycle regardless of source wording while preserving the source wording in monster data and audits:

- Poisoned does not stack.
- Poisoned applies its normal Disadvantage effects.
- poison condition immunity or Protection from Poison prevents application.
- At the start of the poisoned creature's turn, it repeats the source-provided recovery save when one exists; otherwise Iron Pit uses DC 10 Constitution.
- Success ends Poisoned. Failure leaves it active until the next start-of-turn recovery save.
- Poison damage remains source-specific and is resolved normally through universal resistance/immunity/vulnerability rules.

## Arena-neutral examples

Rules with no meaningful effect on a card-v-card combat outcome should be source-audited but require no runtime behavior. Examples include Water Breathing and similar environmental-only capabilities.

## Data ownership

- The SRD/source layer owns printed statistics and wording.
- Shared engine policy owns simulation simplifications.
- Monster and pregen definitions never receive class- or creature-specific resolver functions when a shared mechanic can express the behavior.

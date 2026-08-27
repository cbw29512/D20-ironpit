# Iron Pit D20 — Locked MVP

## Definition of Done

The MVP is complete when a user can open the deployed Netlify site, start a server-resolved duel between **Aldric Vane (Level 1 Fighter)** and the **SRD 5.2.1 Goblin Warrior**, watch the battle replay through stick-figure animation events, and see a winner that matches the FastAPI battle result.

## Required combat behavior

- Secure OS-backed dice rolls.
- Initiative with modifiers.
- Melee attack rolls against Armor Class.
- Natural 1 miss behavior.
- Natural 20 hit and critical weapon dice.
- Damage and HP tracking.
- Combat ends at 0 HP.
- Immutable-style ordered battle event output for replay/audit.

## Required presentation behavior

- Fighter uses a longsword and shield visual loadout.
- Goblin uses a scimitar and shield visual loadout.
- Attack events produce stick-figure weapon swings.
- Hits visibly react and update HP.
- Critical hits receive a distinct animation state.
- Death produces a defeated visual state.

## Required platform behavior

- Source is hosted publicly on GitHub.
- GitHub Actions tests the backend and deployment artifacts.
- Frontend deploys to Netlify.
- FastAPI deploys as a Docker service.
- No secrets are committed.

## Explicitly deferred

- User accounts and Supabase persistence.
- Betting, cash-value predictions, crypto, or NFTs.
- Multiple character levels and classes.
- Character selection UI.
- Monster selection UI.
- Ranged combat.
- Spells and spell effects.
- Conditions such as petrified.
- Breath weapons.
- Advantage/disadvantage.
- Fighter Second Wind and Weapon Mastery.
- Goblin Nimble Escape and conditional bonus damage.

These are expansions after the deployed Fighter-vs-Goblin vertical slice is verified.

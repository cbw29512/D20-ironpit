# Iron Pit D20 — Locked MVP

## Definition of Done

The MVP is complete when a user can open the deployed Netlify site, start a server-resolved duel between **Aldric Vane (Level 1 Fighter)** and the **SRD 5.2.1 Goblin Warrior**, watch the battle replay through stick-figure animation events, and see a winner that matches the FastAPI battle result.

The locked acceptance test remains the **5-foot melee duel**. A separate **90-foot ranged development mode** exercises movement, Dash, weapon selection, range, and projectile replay without changing that acceptance target. Catalog expansion must not weaken this regression target.

## Required combat behavior

- Secure OS-backed dice rolls.
- Initiative with modifiers.
- Melee attack rolls against Armor Class.
- Natural 1 miss behavior.
- Natural 20 hit and critical damage dice.
- Damage and HP tracking.
- Combat ends at 0 HP.
- Immutable-style ordered battle event output for replay/audit.
- Advantage/disadvantage preserves both d20s and the selected result.
- Level-1 Fighter Second Wind: 2 uses, Bonus Action, 1d10 + Fighter level healing, capped at max HP.

## Implemented development extensions

- Data-driven combatant catalog with stable character and monster IDs.
- Catalog rules coverage: `fully_implemented`, `arena_assumption`, or `unsupported`.
- Generic ID-driven `POST /api/battles` endpoint plus character and monster catalog endpoints.
- Gladiator and monster selection controls driven by catalog data.
- SRD Goblin Warrior, Skeleton (CR 1/4), and Ogre (CR 2) catalog entries.
- Typed melee, ranged, and thrown weapon metadata.
- Attack-profile damage dice overrides keep intrinsic equipment dice combatant-neutral.
- Typed damage Vulnerability, Resistance, and Immunity with raw roll and applied damage kept separate.
- SRD Resistance-before-Vulnerability ordering and same-type damage grouping.
- Goblin Shortbow: 80/320 ft., Piercing damage, projectile metadata.
- Ogre Javelin melee/thrown handling at 30/120 ft.
- Ranged/thrown attacks beyond normal range have Disadvantage; attacks beyond long range are illegal.
- Ranged attacks within 5 feet of an active enemy have Disadvantage.
- Goblin attacks made with Advantage add the SRD conditional d4 damage.
- Critical hits double both base and other attack damage dice.
- Speed, remaining movement, Action availability, movement events, and Dash.
- Arena weapon selection prefers the primary weapon, then a legal alternate.
- Optional 90-foot ranged duel endpoint and UI control.

## Required presentation behavior

- Fighter uses a longsword and shield visual loadout.
- Monster labels, HP, CR, weapon, armor, off-hand, and body style hydrate from catalog/API data.
- Goblinoid, skeleton, and giant body styles are visually distinct.
- Monster primary weapon shapes are selected from visual metadata.
- Attack events produce stick-figure weapon swings.
- Projectile attacks animate arrows or thrown javelins in the attack direction.
- Movement events update the displayed distance and animate an advance.
- Hits visibly react and update HP.
- Critical hits receive a distinct animation state.
- Damage defenses preserve the raw roll in the log and show adjusted damage when different.
- Second Wind produces a healing pulse and HP recovery.
- Death produces a defeated visual state.

## Required platform behavior

- Source is hosted publicly on GitHub.
- Active development occurs on `develop`; `main` is reserved for deliberate production releases.
- GitHub Actions tests backend rules, source-size limits, frontend JavaScript syntax, Netlify configuration generation, and the Docker image build.
- Netlify builds are guarded so non-production contexts are skipped.
- Frontend production deploys to Netlify only from an intentional `main` release.
- FastAPI deploys as a Docker service.
- No secrets are committed.

## Published arena assumptions / tactics

- Initiative ties currently use initiative bonus as the arena tiebreaker.
- The demo Fighter uses Second Wind at or below half maximum HP when a use and Bonus Action remain.
- A combatant prefers its primary weapon; if it is out of range, it selects the first legal alternate weapon.
- If no weapon can attack, the combatant advances toward primary-weapon range and Dashes if one normal move is insufficient.
- The Goblin does not yet kite away from the Fighter.
- Ogre Javelin inventory depletion is not yet tracked; its SRD stat block lists three Javelins.

## Explicitly deferred

- User accounts and Supabase persistence.
- Betting, cash-value predictions, crypto, or NFTs.
- Broad character levels and classes.
- Opportunity attacks and Disengage.
- Goblin Nimble Escape/Hide behavior.
- Exhaustion, Poisoned, and other general condition-state handling.
- Cover and terrain.
- Spells and spell effects.
- Conditions such as Petrified.
- Breath weapons.
- Fighter Weapon Mastery effects.
- Finite weapon/ammunition inventory.

These remain expansions after the deployed Fighter-vs-Goblin vertical slice is verified.
